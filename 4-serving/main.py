#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
TẦNG 4: SERVING LAYER – FastAPI REST API
File: main.py
=============================================================================
"""

from contextlib import asynccontextmanager
from datetime import datetime
from typing import AsyncGenerator
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from models.schemas import ApiResponse, HealthStatus, ProvinceWeatherRecord, WeatherSummary
from services.hdfs_reader import HdfsReaderService

hdfs_service = HdfsReaderService()

@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncGenerator[None, None]:
    print("[FastAPI] Đang khởi động Weather Serving Layer...")
    await hdfs_service.refresh_cache()
    yield
    print("[FastAPI] Serving Layer đang tắt...")

app = FastAPI(
    title="Weather Analytics API",
    description="Tầng 4 – Serving Layer: Cung cấp dữ liệu thời tiết và Benchmark.",
    version="2.0.0",
    docs_url="/api/docs",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)

@app.get("/api/health", response_model=HealthStatus)
async def health_check() -> HealthStatus:
    return HealthStatus(
        status="ok",
        timestamp=datetime.utcnow().isoformat() + "Z",
        data_source=hdfs_service.output_base_path,
        records={"weather": len(hdfs_service.get_weather_records())},
    )

@app.get("/api/weather/latest", response_model=ApiResponse[list[ProvinceWeatherRecord]])
async def get_latest_weather() -> ApiResponse[list[ProvinceWeatherRecord]]:
    data = hdfs_service.get_weather_records()
    return ApiResponse(
        success=True,
        data=data,
        count=len(data),
        timestamp=datetime.utcnow().isoformat() + "Z",
        message="Dữ liệu thời tiết mới nhất từ 63 tỉnh thành.",
    )

@app.get("/api/weather/summary", response_model=ApiResponse[WeatherSummary])
async def get_weather_summary() -> ApiResponse[WeatherSummary]:
    data = hdfs_service.get_weather_summary()
    return ApiResponse(
        success=True,
        data=data,
        count=1,
        timestamp=datetime.utcnow().isoformat() + "Z",
        message="Tổng hợp thống kê thời tiết toàn quốc.",
    )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=4000)
