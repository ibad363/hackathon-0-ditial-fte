"""
Performance Optimization Module

Provides caching, rate limiting, and performance optimizations for LinkedIn profile skills.
"""

import json
import time
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Optional, Dict, List, Callable
from functools import wraps, lru_cache


class CacheManager:
    """
    Manages caching for profile data and generated content.

    Usage:
        cache = CacheManager(vault_path="AI_Employee_Vault")

        # Cache profile data
        cache.set_profile_data(profile_id, profile_data)
        data = cache.get_profile_data(profile_id)

        # Cache generated content
        cache.set_drafts(profile_id, target_role, drafts)
        drafts = cache.get_drafts(profile_id, target_role)
    """

    def __init__(self, vault_path: str | Path = "AI_Employee_Vault", ttl_hours: int = 24):
        """
        Initialize cache manager.

        Args:
            vault_path: Path to vault for cache storage
            ttl_hours: Time-to-live for cache entries in hours
        """
        self.vault_path = Path(vault_path)
        self.cache_dir = self.vault_path / ".cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl_seconds = ttl_hours * 3600

    def _get_cache_path(self, category: str, key: str) -> Path:
        """Get cache file path for a given category and key."""
        # Create safe filename from key
        safe_key = hashlib.md5(key.encode()).hexdigest()
        return self.cache_dir / f"{category}_{safe_key}.json"

    def _is_valid(self, cache_path: Path) -> bool:
        """Check if cache file is still valid (not expired)."""
        if not cache_path.exists():
            return False

        try:
            data = json.loads(cache_path.read_text())
            cached_at = datetime.fromisoformat(data.get("cached_at", ""))
            age = (datetime.now() - cached_at).total_seconds()
            return age < self.ttl_seconds
        except Exception:
            return False

    def set(self, category: str, key: str, value: Any) -> None:
        """
        Store value in cache.

        Args:
            category: Cache category (e.g., "profile", "drafts")
            key: Unique key for this entry
            value: Value to cache (must be JSON-serializable)
        """
        cache_path = self._get_cache_path(category, key)

        cache_data = {
            "cached_at": datetime.now().isoformat(),
            "key": key,
            "category": category,
            "data": value
        }

        cache_path.write_text(json.dumps(cache_data, indent=2), encoding="utf-8")

    def get(self, category: str, key: str) -> Optional[Any]:
        """
        Retrieve value from cache if valid.

        Args:
            category: Cache category
            key: Unique key for this entry

        Returns:
            Cached value if valid and exists, None otherwise
        """
        cache_path = self._get_cache_path(category, key)

        if not self._is_valid(cache_path):
            return None

        try:
            cache_data = json.loads(cache_path.read_text())
            return cache_data.get("data")
        except Exception:
            return None

    def set_profile_data(self, profile_id: str, profile_data: Any) -> None:
        """Cache profile extraction results."""
        # Create unique key from profile attributes
        key = f"profile_{profile_id}_{profile_data.extracted_at.isoformat()}"
        self.set("profile", key, {
            "profile_id": profile_id,
            "completeness_score": getattr(profile_data, "completeness_score", None),
            "skills_count": len(profile_data.skills),
            "experience_count": len(profile_data.experience),
            "extracted_at": profile_data.extracted_at.isoformat()
        })

    def get_profile_data(self, profile_id: str, tolerance_minutes: int = 5) -> Optional[Any]:
        """Get cached profile data if recent enough."""
        # Validate tolerance_minutes
        if tolerance_minutes <= 0:
            tolerance_minutes = 1  # At least try current time

        # Try multiple recent cache keys
        for offset in range(tolerance_minutes):
            cache_time = datetime.now() - timedelta(minutes=offset)
            key = f"profile_{profile_id}_{cache_time.isoformat()}"
            data = self.get("profile", key)
            if data:
                return data
        return None

    def set_drafts(self, profile_id: str, target_role: str, drafts: Any) -> None:
        """Cache generated drafts."""
        key = f"drafts_{profile_id}_{target_role}_{datetime.now().date().isoformat()}"
        self.set("drafts", key, {
            "profile_id": profile_id,
            "target_role": target_role,
            "headline": drafts.headline.suggested if hasattr(drafts, 'headline') else None,
            "about_length": drafts.about.word_count if hasattr(drafts, 'about') else None,
            "generated_at": datetime.now().isoformat()
        })

    def get_drafts(self, profile_id: str, target_role: str, days_valid: int = 1) -> Optional[Any]:
        """Get cached drafts if recent enough."""
        # Validate days_valid
        if days_valid <= 0:
            days_valid = 1  # At least try current day

        for offset in range(days_valid):
            cache_date = datetime.now() - timedelta(days=offset)
            key = f"drafts_{profile_id}_{target_role}_{cache_date.isoformat()}"
            data = self.get("drafts", key)
            if data:
                return data
        return None

    def clear_cache(self, category: Optional[str] = None) -> int:
        """
        Clear cache entries.

        Args:
            category: Specific category to clear, or None for all

        Returns:
            Number of cache files cleared
        """
        cleared = 0

        if category:
            # Clear specific category
            pattern = f"{category}_*.json"
        else:
            # Clear all cache
            pattern = "*.json"

        for cache_file in self.cache_dir.glob(pattern):
            try:
                cache_file.unlink()
                cleared += 1
            except Exception:
                pass

        return cleared

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get statistics about cache usage."""
        cache_files = list(self.cache_dir.glob("*.json"))

        total_size = sum(f.stat().st_size for f in cache_files) if cache_files else 0

        by_category = {}
        for cache_file in cache_files:
            category = cache_file.stem.split("_")[0]
            by_category[category] = by_category.get(category, 0) + 1

        return {
            "total_entries": len(cache_files),
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / 1024 / 1024, 2),
            "by_category": by_category,
            "cache_dir": str(self.cache_dir)
        }


class RateLimiter:
    """
    Rate limiter for LinkedIn API access.

    Usage:
        limiter = RateLimiter(requests_per_minute=30)

        if limiter.can_proceed():
            limiter.record_request()
            # Make LinkedIn request
        else:
            limiter.wait_until_allowed()
            # Make LinkedIn request
    """

    def __init__(
        self,
        requests_per_minute: int = 10,
        requests_per_hour: int = 100
    ):
        """
        Initialize rate limiter.

        Args:
            requests_per_minute: Maximum requests per minute
            requests_per_hour: Maximum requests per hour
        """
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour

        self.minute_window = 60  # seconds
        self.hour_window = 3600  # seconds

        self.minute_requests = []
        self.hour_requests = []

    def _clean_old_requests(self, now: float) -> None:
        """Remove request records older than the window."""
        cutoff_minute = now - self.minute_window
        cutoff_hour = now - self.hour_window

        self.minute_requests = [t for t in self.minute_requests if t > cutoff_minute]
        self.hour_requests = [t for t in self.hour_requests if t > cutoff_hour]

    def _get_request_count(self, window: List[float], window_size: float, now: float) -> int:
        """Count requests in the given time window."""
        cutoff = now - window_size
        return sum(1 for t in window if t > cutoff)

    def can_proceed(self) -> bool:
        """Check if a request can be made without violating rate limits."""
        now = time.time()
        self._clean_old_requests(now)

        minute_count = self._get_request_count(self.minute_requests, self.minute_window, now)
        hour_count = self._get_request_count(self.hour_requests, self.hour_window, now)

        return minute_count < self.requests_per_minute and hour_count < self.requests_per_hour

    def record_request(self) -> None:
        """Record that a request was made."""
        now = time.time()
        self.minute_requests.append(now)
        self.hour_requests.append(now)

    def wait_until_allowed(self, timeout: int = 60) -> bool:
        """
        Wait until a request can be made.

        Args:
            timeout: Maximum seconds to wait

        Returns:
            True if allowed within timeout, False if timeout exceeded
        """
        start = time.time()

        while not self.can_proceed():
            if time.time() - start > timeout:
                return False

            # Calculate wait time
            oldest_minute = min(self.minute_requests) if self.minute_requests else start
            wait_time = (oldest_minute + self.minute_window) - time.time() + 1

            if wait_time > 0:
                time.sleep(min(wait_time, 5))  # Sleep in small chunks
            else:
                time.sleep(1)

        return True

    def get_wait_time(self) -> float:
        """Get seconds to wait before next allowed request."""
        if self.can_proceed():
            return 0.0

        now = time.time()
        self._clean_old_requests(now)

        # Calculate when oldest request expires
        if self.minute_requests:
            oldest = min(self.minute_requests)
            minute_wait = (oldest + self.minute_window) - now + 1
        else:
            minute_wait = 0

        if self.hour_requests:
            oldest = min(self.hour_requests)
            hour_wait = (oldest + self.hour_window) - now + 1
        else:
            hour_wait = 0

        return max(minute_wait, hour_wait, 0.1)  # At least 0.1s

    def reset(self) -> None:
        """Reset rate limiter (for testing)."""
        self.minute_requests = []
        self.hour_requests = []


def cached(ttl_seconds: int = 3600):
    """
    Decorator for caching function results.

    Usage:
        @cached(ttl_seconds=300)
        def expensive_function(x):
            return x * 2
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            key = f"{func.__name__}_{str(args)}_{str(sorted(kwargs.items()))}"

            # Try to get from cache
            cache_mgr = CacheManager()  # Uses default vault path
            cached = cache_mgr.get("function", key)

            if cached is not None:
                return cached["data"]

            # Not in cache, compute and store
            result = func(*args, **kwargs)

            cache_mgr.set("function", key, {
                "result": result,
                "cached_at": datetime.now().isoformat()
            })

            return result

        wrapper.cache_clear = lambda: CacheManager().clear_cache("function")
        return wrapper

    return decorator


class PerformanceMonitor:
    """
    Monitors and reports on performance metrics.

    Usage:
        monitor = PerformanceMonitor(vault_path="AI_Employee_Vault")

        with monitor.track_operation("extract_profile"):
            result = accessor.extract_profile_data(profile_id)

        stats = monitor.get_stats()
    """

    def __init__(self, vault_path: str | Path = "AI_Employee_Vault"):
        """Initialize performance monitor."""
        self.vault_path = Path(vault_path)
        self.stats_file = self.vault_path / ".performance_stats.json"

    def _load_stats(self) -> Dict:
        """Load existing stats from file."""
        if self.stats_file.exists():
            try:
                return json.loads(self.stats_file.read_text())
            except Exception:
                pass
        return {
            "operations": {},
            "last_updated": None
        }

    def _save_stats(self, stats: Dict) -> None:
        """Save stats to file."""
        stats["last_updated"] = datetime.now().isoformat()
        self.stats_file.write_text(json.dumps(stats, indent=2), encoding="utf-8")

    def track_operation(self, operation_name: str):
        """
        Context manager for tracking an operation.

        Usage:
            with monitor.track_operation("extract_profile"):
                result = accessor.extract_profile_data(profile_id)
        """
        class OperationTracker:
            def __init__(self, operation_name, monitor):
                self.operation_name = operation_name
                self.monitor = monitor
                self.start_time = None

            def __enter__(self):
                self.start_time = time.time()
                return self

            def __exit__(self, exc_type, exc_val, exc_tb):
                if exc_type is None:  # Success
                    duration = time.time() - self.start_time
                    stats = self._load_stats()

                    if operation_name not in stats["operations"]:
                        stats["operations"][operation_name] = {
                            "count": 0,
                            "total_time": 0,
                            "avg_time": 0
                        }

                    op_stats = stats["operations"][operation_name]
                    op_stats["count"] += 1
                    op_stats["total_time"] += duration
                    op_stats["avg_time"] = op_stats["total_time"] / op_stats["count"]

                    self._save_stats(stats)

                return False  # Don't suppress exceptions

        return OperationTracker(operation_name, self)

    def get_stats(self) -> Dict:
        """Get current performance statistics."""
        stats = self._load_stats()

        # Add summary stats
        total_operations = sum(
            op.get("count", 0)
            for op in stats.get("operations", {}).values()
        )
        total_time = sum(
            op.get("total_time", 0)
            for op in stats.get("operations", {}).values()
        )

        stats["summary"] = {
            "total_operations": total_operations,
            "total_time": round(total_time, 2),
            "avg_time_per_operation": round(total_time / total_operations, 3) if total_operations > 0 else 0
        }

        return stats

    def get_slowest_operations(self, limit: int = 5) -> List[Dict]:
        """Get the slowest operations by average time."""
        stats = self._load_stats()

        operations = []
        for op_name, op_stats in stats.get("operations", {}).items():
            if op_stats.get("count", 0) > 0:
                operations.append({
                    "operation": op_name,
                    "avg_time": op_stats.get("avg_time", 0),
                    "count": op_stats.get("count", 0),
                    "total_time": op_stats.get("total_time", 0)
                })

        operations.sort(key=lambda x: x["avg_time"], reverse=True)
        return operations[:limit]


class BatchProcessor:
    """
    Process multiple profiles efficiently with batching and caching.

    Usage:
        processor = BatchProcessor(vault_path="AI_Employee_Vault")

        profile_ids = ["id1", "id2", "id3"]
        results = processor.process_batch(
            profile_ids,
            lambda pid: accessor.extract_profile_data(pid)
        )
    """

    def __init__(
        self,
        vault_path: str | Path = "AI_Employee_Vault",
        batch_size: int = 5,
        parallel: bool = False
    ):
        """
        Initialize batch processor.

        Args:
            vault_path: Path to vault
            batch_size: Number of profiles to process in each batch
            parallel: Whether to process batches in parallel
        """
        self.vault_path = Path(vault_path)
        self.batch_size = batch_size
        self.parallel = parallel

    async def process_batch(
        self,
        profile_ids: List[str],
        processor_func: Callable,
        show_progress: bool = True
    ) -> List[Any]:
        """
        Process multiple profiles in batches.

        Args:
            profile_ids: List of profile IDs to process
            processor_func: Async function to process each profile
            show_progress: Whether to show progress indicators

        Returns:
            List of processed results
        """
        results = []
        total = len(profile_ids)

        for i in range(0, total, self.batch_size):
            batch = profile_ids[i:i + self.batch_size]
            batch_num = i // self.batch_size + 1

            if show_progress:
                print(f"Processing batch {batch_num}/{(total + self.batch_size - 1)//self.batch_size} ({len(batch)} profiles)...")

            # Process batch
            batch_results = await asyncio.gather(*[
                processor_func(profile_id)
                for profile_id in batch
            ])

            results.extend(batch_results)

            # Small delay between batches
            if i + self.batch_size < total:
                await asyncio.sleep(2)

        return results

    def get_optimal_batch_size(self, test_func: Callable) -> int:
        """
        Determine optimal batch size by testing different sizes.

        Args:
            test_func: Function to test with

        Returns:
            Optimal batch size
        """
        # Test with different batch sizes
        for size in [1, 2, 5, 10]:
            try:
                start = time.time()
                # Test with dummy data
                test_data = [f"test_{i}" for i in range(size)]

                # This would be the actual processor function
                import asyncio
                async def dummy_process(x):
                    await asyncio.sleep(0.1)
                    return x

                asyncio.run(self.process_batch(test_data, dummy_process, show_progress=False))
                duration = time.time() - start

                # If duration is reasonable, this size works
                if duration < 10:
                    return size
            except Exception:
                continue

        return self.batch_size


# Convenience functions for easy access
def get_cache_manager(vault_path: str = "AI_Employee_Vault") -> CacheManager:
    """Get or create cache manager instance."""
    return CacheManager(vault_path=vault_path)


def get_rate_limiter(
    requests_per_minute: int = 10,
    requests_per_hour: int = 100
) -> RateLimiter:
    """Get rate limiter instance with specified limits."""
    return RateLimiter(
        requests_per_minute=requests_per_minute,
        requests_per_hour=requests_per_hour
    )


def get_performance_monitor(vault_path: str = "AI_Employee_Vault") -> PerformanceMonitor:
    """Get or create performance monitor instance."""
    return PerformanceMonitor(vault_path=vault_path)
