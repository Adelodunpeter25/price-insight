"""Monitoring and metrics system."""

import time
from datetime import datetime
from typing import Dict, List

from loguru import logger

from app.core.job_manager import job_manager
from app.core.scheduler import scheduler_manager


class MonitoringService:
    """Service for monitoring application health and performance."""

    def __init__(self):
        """Initialize monitoring service."""
        self.metrics = {
            "scraping_jobs": {"total": 0, "successful": 0, "failed": 0},
            "alerts_sent": {"total": 0, "by_type": {}},
            "api_requests": {"total": 0, "by_endpoint": {}},
            "response_times": [],
        }
        self.start_time = datetime.utcnow()

    def record_scraping_job(self, success: bool, duration: float, products_scraped: int):
        """Record scraping job metrics."""
        self.metrics["scraping_jobs"]["total"] += 1
        if success:
            self.metrics["scraping_jobs"]["successful"] += 1
        else:
            self.metrics["scraping_jobs"]["failed"] += 1

        logger.info(
            f"Scraping job completed: success={success}, "
            f"duration={duration:.2f}s, products={products_scraped}"
        )

    def record_alert_sent(self, alert_type: str):
        """Record alert metrics."""
        self.metrics["alerts_sent"]["total"] += 1
        if alert_type not in self.metrics["alerts_sent"]["by_type"]:
            self.metrics["alerts_sent"]["by_type"][alert_type] = 0
        self.metrics["alerts_sent"]["by_type"][alert_type] += 1

        logger.info(f"Alert sent: type={alert_type}")

    def record_api_request(self, endpoint: str, response_time: float):
        """Record API request metrics."""
        self.metrics["api_requests"]["total"] += 1
        if endpoint not in self.metrics["api_requests"]["by_endpoint"]:
            self.metrics["api_requests"]["by_endpoint"][endpoint] = 0
        self.metrics["api_requests"]["by_endpoint"][endpoint] += 1

        self.metrics["response_times"].append(response_time)
        # Keep only last 1000 response times
        if len(self.metrics["response_times"]) > 1000:
            self.metrics["response_times"] = self.metrics["response_times"][-1000:]

    def get_health_status(self) -> Dict:
        """Get overall application health status."""
        uptime = (datetime.utcnow() - self.start_time).total_seconds()

        # Calculate success rate
        scraping_total = self.metrics["scraping_jobs"]["total"]
        scraping_success_rate = (
            (self.metrics["scraping_jobs"]["successful"] / scraping_total * 100)
            if scraping_total > 0
            else 0
        )

        # Calculate average response time
        response_times = self.metrics["response_times"]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0

        return {
            "status": "healthy" if scraping_success_rate > 50 else "degraded",
            "uptime_seconds": uptime,
            "scheduler_running": scheduler_manager.is_running,
            "total_jobs": len(job_manager.get_job_status()),
            "scraping_success_rate": round(scraping_success_rate, 2),
            "total_alerts_sent": self.metrics["alerts_sent"]["total"],
            "total_api_requests": self.metrics["api_requests"]["total"],
            "avg_response_time_ms": round(avg_response_time * 1000, 2),
        }

    def get_detailed_metrics(self) -> Dict:
        """Get detailed metrics for monitoring dashboard."""
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "uptime_seconds": (datetime.utcnow() - self.start_time).total_seconds(),
            "scraping_metrics": self.metrics["scraping_jobs"],
            "alert_metrics": self.metrics["alerts_sent"],
            "api_metrics": self.metrics["api_requests"],
            "performance_metrics": {
                "avg_response_time_ms": (
                    round(sum(self.metrics["response_times"]) / len(self.metrics["response_times"]) * 1000, 2)
                    if self.metrics["response_times"]
                    else 0
                ),
                "total_requests": len(self.metrics["response_times"]),
            },
            "scheduler_status": {
                "running": scheduler_manager.is_running,
                "jobs": job_manager.get_job_status(),
            },
        }

    def log_performance_summary(self):
        """Log performance summary."""
        health = self.get_health_status()
        logger.info(f"📊 Performance Summary:")
        logger.info(f"   Status: {health['status']}")
        logger.info(f"   Uptime: {health['uptime_seconds']:.0f}s")
        logger.info(f"   Scraping Success Rate: {health['scraping_success_rate']}%")
        logger.info(f"   Total Alerts: {health['total_alerts_sent']}")
        logger.info(f"   Avg Response Time: {health['avg_response_time_ms']}ms")


# Global monitoring service instance
monitoring_service = MonitoringService()


class PerformanceTimer:
    """Context manager for timing operations."""

    def __init__(self, operation_name: str):
        """Initialize timer."""
        self.operation_name = operation_name
        self.start_time = None

    def __enter__(self):
        """Start timing."""
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """End timing and log result."""
        duration = time.time() - self.start_time
        if exc_type is None:
            logger.info(f"⏱️  {self.operation_name} completed in {duration:.2f}s")
        else:
            logger.error(f"❌ {self.operation_name} failed after {duration:.2f}s: {exc_val}")
        return False