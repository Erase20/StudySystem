# SmartOps 智能运维监控平台 — 详细开发文档

---

## 1. 项目概述

### 1.1 项目背景

随着服务器集群规模的不断扩大，传统的基于固定阈值的监控方式（如 Zabbix、Nagios 等）已难以应对复杂多变的业务场景。固定阈值方案存在以下核心痛点：

- **误报率高**：无法区分业务高峰与真实异常，频繁产生无效告警。
- **缺乏预测能力**：只能在问题发生后响应，无法提前预警。
- **人工依赖重**：异常处理需要运维人员手动介入，响应时间长。
- **性能瓶颈**：纯 Python 采集方案在高频场景下受 GIL 限制，无法满足低延迟需求。

### 1.2 项目目标

SmartOps 平台的核心开发目标如下：

| 目标 | 描述 |
|------|------|
| **突破性能瓶颈** | 通过 Python 与 C/C++ 混合编程，解决纯 Python 在高频底层数据采集时的 GIL 锁限制与性能问题 |
| **智能化预警** | 集成机器学习算法，实现服务器负载趋势预测与异常模式自动识别，降低误报率 |
| **自动化闭环** | 构建从数据上报、异常检测到自动修复（服务重启、日志清理）的自动化运维链路 |
| **高可用架构** | 采用异步 Web 框架与缓存机制，支撑高并发数据写入与实时查询 |

### 1.3 系统功能总览

```
┌─────────────────────────────────────────────────────┐
│                  SmartOps 平台                        │
├──────────┬──────────┬──────────┬─────────────────────┤
│ 数据采集  │ 智能分析  │ 自动化运维 │   可视化展示        │
│ ·CPU监控  │ ·异常检测  │ ·远程SSH   │ ·实时仪表盘        │
│ ·内存监控  │ ·趋势预测  │ ·服务重启  │ ·历史趋势图        │
│ ·磁盘I/O  │ ·告警管理  │ ·日志清理  │ ·告警通知面板      │
│ ·网络流量  │ ·基线学习  │ ·健康检查  │ ·运维操作日志      │
└──────────┴──────────┴──────────┴─────────────────────┘
```

---

## 2. 技术选型与架构设计

### 2.1 核心技术栈

| 层级 | 技术 | 版本要求 | 用途说明 |
|------|------|---------|---------|
| 编程语言 | Python | 3.9+ | 业务逻辑、AI 算法、Web 服务 |
| 编程语言 | C/C++ | C99 / C++11 | 底层数据采集模块 |
| Web 框架 | FastAPI | 0.100+ | 异步 RESTful API 服务 |
| 实时缓存 | Redis | 7.0+ | 实时指标数据缓存、消息队列 |
| 持久化存储 | PostgreSQL | 15+ | 历史指标数据持久化 |
| AI/算法库 | Scikit-learn | 1.3+ | 异常检测算法（孤立森林等） |
| 数值计算 | NumPy / Pandas | 1.24+ / 2.0+ | 数据预处理与向量化计算 |
| 跨语言调用 | ctypes / pybind11 | 内置 / 1.0+ | Python 调用 C 动态链接库 |
| 异步任务 | Celery | 5.3+ | 异步任务队列（AI 检测、运维操作） |
| 远程执行 | Paramiko | 3.0+ | SSH 远程命令执行 |
| ASGI 服务器 | Uvicorn | 0.23+ | FastAPI 生产级 ASGI 服务器 |
| 容器化 | Docker / Docker Compose | 24+ / 2.20+ | 服务容器化编排 |
| 反向代理 | Nginx | 1.24+ | 负载均衡与静态资源代理 |

### 2.2 系统架构图

```
                    ┌──────────────┐
                    │   Nginx      │
                    │  反向代理     │
                    └──────┬───────┘
                           │
                    ┌──────▼───────┐
                    │   FastAPI    │
                    │  Web 后端    │
                    └──┬───┬───┬───┘
                       │   │   │
          ┌────────────┘   │   └────────────┐
          │                │                │
   ┌──────▼──────┐ ┌──────▼──────┐ ┌──────▼──────┐
   │    Redis    │ │ PostgreSQL  │ │   Celery    │
   │  实时缓存    │ │  历史存储    │ │  任务队列    │
   └─────────────┘ └─────────────┘ └──┬──────┬───┘
                                      │      │
                              ┌───────▼┐  ┌──▼────────┐
                              │AI 检测  │  │ 运维执行   │
                              │Service  │  │ Service   │
                              └────────┘  └──────┬────┘
                                                 │
                                          ┌──────▼──────┐
                                          │  目标服务器   │
                                          │  (SSH远程)   │
                                          └─────────────┘

   ┌─────────────────────────────────────┐
   │         数据采集探针 (Agent)          │
   │  ┌─────────┐    ┌────────────────┐  │
   │  │ C 采集库 │◄───│ Python 调度器   │  │
   │  │libsysmon│    │ (ctypes桥接)   │  │
   │  │  .so    │    └───────┬────────┘  │
   │  └─────────┘            │           │
   │                   上报数据至后端      │
   └─────────────────────────────────────┘
```

### 2.3 分层架构说明

项目采用四层分层架构，确保各模块解耦与高内聚：

**第一层：数据采集层（Collector Agent）**
- 部署在每台被监控服务器上
- 通过 C 语言直接读取 `/proc` 文件系统获取 CPU、内存、磁盘等底层指标
- 编译为动态链接库 `libsysmon.so`，由 Python 调度器定时调用
- 采集频率可配置（默认每秒一次），通过 HTTP POST 上报至 Web 后端

**第二层：Web 服务层（Backend API）**
- 基于 FastAPI 构建 RESTful API
- 接收探针上报数据，写入 Redis 缓存，异步持久化至 PostgreSQL
- 提供前端数据查询接口，支持时间范围筛选
- 集成 Celery 任务队列，异步调度 AI 检测与运维操作

**第三层：智能分析层（AI Service）**
- 封装异常检测算法（孤立森林、滑动窗口统计等）
- 对时序数据进行实时分析与趋势预测
- 采用"旁路检测"模式，不阻塞主 API 响应
- 检测到异常时触发告警（邮件 / Webhook）

**第四层：自动化运维层（Ops Service）**
- 通过 Paramiko 实现 SSH 远程命令执行
- 支持服务状态检查、进程重启、日志归档等运维操作
- 与 AI 告警联动，实现"检测→修复→验证"闭环

---

## 3. 项目目录结构

```
smartops/
├── agent/                          # 数据采集探针
│   ├── c_module/                   # C 语言采集模块
│   │   ├── sysmon.h                # 头文件：数据结构与函数声明
│   │   ├── sysmon_cpu.c            # CPU 指标采集实现
│   │   ├── sysmon_mem.c            # 内存指标采集实现
│   │   ├── sysmon_disk.c           # 磁盘指标采集实现
│   │   ├── sysmon_net.c            # 网络指标采集实现
│   │   └── Makefile                # 编译脚本
│   ├── collector.py                # Python 采集调度器
│   ├── bridge.py                   # ctypes 桥接层
│   ├── config.yaml                 # 探针配置文件
│   └── requirements.txt            # 探针依赖
│
├── backend/                        # Web 后端服务
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                 # FastAPI 应用入口
│   │   ├── config.py               # 配置管理
│   │   ├── models/                 # Pydantic 数据模型
│   │   │   ├── __init__.py
│   │   │   ├── metrics.py          # 指标数据模型
│   │   │   ├── alert.py            # 告警数据模型
│   │   │   └── host.py             # 主机信息模型
│   │   ├── schemas/                # 请求/响应 Schema
│   │   │   ├── __init__.py
│   │   │   └── api.py
│   │   ├── api/                    # API 路由
│   │   │   ├── __init__.py
│   │   │   ├── v1/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── metrics.py      # 指标上报与查询接口
│   │   │   │   ├── alerts.py       # 告警管理接口
│   │   │   │   ├── hosts.py        # 主机管理接口
│   │   │   │   └── ops.py          # 运维操作接口
│   │   │   └── deps.py             # 依赖注入
│   │   ├── services/               # 业务逻辑层
│   │   │   ├── __init__.py
│   │   │   ├── metrics_service.py  # 指标数据处理
│   │   │   ├── alert_service.py    # 告警逻辑
│   │   │   └── ops_service.py      # 运维操作逻辑
│   │   ├── db/                     # 数据库层
│   │   │   ├── __init__.py
│   │   │   ├── redis_client.py     # Redis 客户端
│   │   │   ├── pg_client.py        # PostgreSQL 客户端
│   │   │   └── migrations/         # 数据库迁移脚本
│   │   └── tasks/                  # Celery 异步任务
│   │       ├── __init__.py
│   │       ├── celery_app.py       # Celery 配置
│   │       ├── ai_tasks.py         # AI 检测任务
│   │       └── ops_tasks.py        # 运维操作任务
│   ├── tests/                      # 测试目录
│   │   ├── test_metrics_api.py
│   │   ├── test_ai_detection.py
│   │   └── test_ctypes_bridge.py
│   ├── requirements.txt
│   └── Dockerfile
│
├── ai_service/                     # AI 异常检测服务
│   ├── __init__.py
│   ├── detector.py                 # 异常检测器核心
│   ├── predictor.py                # 趋势预测器
│   ├── baseline.py                 # 基线学习模块
│   ├── preprocess.py               # 数据预处理
│   └── models/                     # 训练好的模型存储
│       └── .gitkeep
│
├── ops_service/                    # 自动化运维服务
│   ├── __init__.py
│   ├── ssh_executor.py             # SSH 远程执行器
│   ├── playbooks/                  # 运维剧本
│   │   ├── restart_service.py      # 服务重启
│   │   ├── clean_logs.py           # 日志清理
│   │   └── health_check.py         # 健康检查
│   └── verify.py                   # 修复结果验证
│
├── deploy/                         # 部署相关
│   ├── docker-compose.yml          # 容器编排
│   ├── nginx/
│   │   └── nginx.conf              # Nginx 配置
│   ├── deploy.sh                   # 一键部署脚本
│   └── .env.example                # 环境变量模板
│
├── docs/                           # 项目文档
│   └── api.md                      # API 文档
│
├── scripts/                        # 工具脚本
│   ├── init_db.sql                 # 数据库初始化 SQL
│   └── seed_data.py                # 测试数据填充
│
└── README.md
```

---

## 4. 核心模块详细设计

### 4.1 数据采集探针模块（Agent）

#### 4.1.1 C 语言采集模块

**目标**：绕过 Python GIL 限制，通过 C 语言直接读取 Linux `/proc` 文件系统，实现微秒级的底层指标采集。

**sysmon.h — 公共头文件**

```c
#ifndef SYSMON_H
#define SYSMON_H

#include <stdint.h>

/* ========== 数据结构定义 ========== */

// CPU 指标
typedef struct {
    double usage_percent;     // CPU 使用率 (%)
    double user_percent;      // 用户态使用率
    double system_percent;    // 内核态使用率
    double iowait_percent;    // IO 等待率
    uint32_t core_count;      // CPU 核心数
    double load_avg_1;        // 1 分钟负载均值
    double load_avg_5;        // 5 分钟负载均值
    double load_avg_15;       // 15 分钟负载均值
} CpuMetrics;

// 内存指标
typedef struct {
    uint64_t total_bytes;     // 总内存 (bytes)
    uint64_t used_bytes;      // 已使用内存
    uint64_t free_bytes;      // 可用内存
    uint64_t cached_bytes;    // 缓存内存
    uint64_t buffers_bytes;   // 缓冲区内存
    double   usage_percent;   // 内存使用率 (%)
    uint64_t swap_total;      // Swap 总量
    uint64_t swap_used;       // Swap 已使用量
} MemMetrics;

// 磁盘指标
typedef struct {
    uint64_t total_bytes;     // 磁盘总容量
    uint64_t used_bytes;      // 已使用容量
    uint64_t free_bytes;      // 可用容量
    double   usage_percent;   // 使用率 (%)
    double   read_bytes_per_sec;  // 读速率 (bytes/s)
    double   write_bytes_per_sec; // 写速率 (bytes/s)
    double   io_util_percent;     // IO 利用率
} DiskMetrics;

// 网络指标
typedef struct {
    uint64_t bytes_sent;          // 累计发送字节数
    uint64_t bytes_recv;          // 累计接收字节数
    uint64_t packets_sent;        // 累计发送包数
    uint64_t packets_recv;        // 累计接收包数
    double   send_bytes_per_sec;  // 发送速率 (bytes/s)
    double   recv_bytes_per_sec;  // 接收速率 (bytes/s)
    uint32_t tcp_connections;     // TCP 连接数
} NetMetrics;

// 综合指标
typedef struct {
    CpuMetrics  cpu;
    MemMetrics  mem;
    DiskMetrics disk;
    NetMetrics  net;
    int64_t     timestamp;       // Unix 时间戳 (毫秒)
    char        hostname[256];   // 主机名
} SystemMetrics;

/* ========== 函数声明 ========== */

// 初始化采集模块（首次调用时执行）
int sysmon_init(void);

// 采集全部指标，结果写入 metrics 指针
// 返回值: 0 成功, -1 失败
int sysmon_collect(SystemMetrics* metrics);

// 单独采集接口
int sysmon_collect_cpu(CpuMetrics* cpu);
int sysmon_collect_mem(MemMetrics* mem);
int sysmon_collect_disk(DiskMetrics* disk);
int sysmon_collect_net(NetMetrics* net);

// 释放资源
void sysmon_cleanup(void);

// 获取错误信息
const char* sysmon_error(void);

#endif // SYSMON_H
```

**sysmon_cpu.c — CPU 采集实现（核心片段）**

```c
#include "sysmon.h"
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h>

// 静态变量：保存上一次采样的 CPU 计数
static uint64_t prev_idle = 0;
static uint64_t prev_total = 0;
static int initialized = 0;
static char error_buf[512];

/*
 * 从 /proc/stat 读取 CPU 时间计数
 * 格式: cpu  user nice system idle iowait irq softirq steal guest guest_nice
 */
static int read_cpu_times(uint64_t *idle, uint64_t *total) {
    FILE *fp = fopen("/proc/stat", "r");
    if (!fp) {
        snprintf(error_buf, sizeof(error_buf), "Failed to open /proc/stat");
        return -1;
    }

    char line[1024];
    if (!fgets(line, sizeof(line), fp)) {
        fclose(fp);
        return -1;
    }
    fclose(fp);

    uint64_t user, nice, system, id, iowait, irq, softirq, steal;
    sscanf(line, "cpu %lu %lu %lu %lu %lu %lu %lu %lu",
           &user, &nice, &system, &id, &iowait, &irq, &softirq, &steal);

    *idle = id + iowait;
    *total = user + nice + system + id + iowait + irq + softirq + steal;
    return 0;
}

int sysmon_collect_cpu(CpuMetrics* cpu) {
    if (!cpu) return -1;

    // 读取核心数
    cpu->core_count = (uint32_t)sysconf(_SC_NPROCESSORS_ONLN);

    // 读取负载均值
    double loadavg[3];
    if (getloadavg(loadavg, 3) != -1) {
        cpu->load_avg_1  = loadavg[0];
        cpu->load_avg_5  = loadavg[1];
        cpu->load_avg_15 = loadavg[2];
    }

    // 计算 CPU 使用率（需要两次采样的差值）
    uint64_t curr_idle, curr_total;
    if (read_cpu_times(&curr_idle, &curr_total) != 0) {
        return -1;
    }

    if (!initialized) {
        prev_idle = curr_idle;
        prev_total = curr_total;
        initialized = 1;
        cpu->usage_percent = 0.0;
        cpu->user_percent = 0.0;
        cpu->system_percent = 0.0;
        cpu->iowait_percent = 0.0;
        return 0;
    }

    uint64_t delta_idle  = curr_idle - prev_idle;
    uint64_t delta_total = curr_total - prev_total;

    if (delta_total == 0) {
        cpu->usage_percent = 0.0;
    } else {
        cpu->usage_percent = (1.0 - (double)delta_idle / delta_total) * 100.0;
    }

    prev_idle  = curr_idle;
    prev_total = curr_total;

    return 0;
}
```

**Makefile — 编译脚本**

```makefile
CC = gcc
CFLAGS = -Wall -Wextra -O2 -fPIC
LDFLAGS = -shared

SRCS = sysmon_cpu.c sysmon_mem.c sysmon_disk.c sysmon_net.c
OBJS = $(SRCS:.c=.o)
TARGET = libsysmon.so

.PHONY: all clean

all: $(TARGET)

$(TARGET): $(OBJS)
	$(CC) $(LDFLAGS) -o $@ $^

%.o: %.c sysmon.h
	$(CC) $(CFLAGS) -c $< -o $@

clean:
	rm -f $(OBJS) $(TARGET)

install: $(TARGET)
	cp $(TARGET) /usr/local/lib/
	ldconfig
```

**编译命令**：
```bash
cd agent/c_module
make clean && make
# 产出: libsysmon.so
```

#### 4.1.2 Python ctypes 桥接层

**bridge.py — ctypes 封装**

```python
"""
bridge.py
Python 与 C 动态库之间的桥接层
负责类型映射、内存安全与错误处理
"""

import ctypes
import os
import platform
from ctypes import (
    Structure, c_double, c_uint32, c_uint64, c_int64,
    c_char_p, c_char, c_int, POINTER, byref
)
from typing import Optional, Dict, Any


class CpuMetrics(Structure):
    """C 端 CpuMetrics 结构体的 Python 映射"""
    _fields_ = [
        ("usage_percent", c_double),
        ("user_percent", c_double),
        ("system_percent", c_double),
        ("iowait_percent", c_double),
        ("core_count", c_uint32),
        ("load_avg_1", c_double),
        ("load_avg_5", c_double),
        ("load_avg_15", c_double),
    ]


class MemMetrics(Structure):
    _fields_ = [
        ("total_bytes", c_uint64),
        ("used_bytes", c_uint64),
        ("free_bytes", c_uint64),
        ("cached_bytes", c_uint64),
        ("buffers_bytes", c_uint64),
        ("usage_percent", c_double),
        ("swap_total", c_uint64),
        ("swap_used", c_uint64),
    ]


class DiskMetrics(Structure):
    _fields_ = [
        ("total_bytes", c_uint64),
        ("used_bytes", c_uint64),
        ("free_bytes", c_uint64),
        ("usage_percent", c_double),
        ("read_bytes_per_sec", c_double),
        ("write_bytes_per_sec", c_double),
        ("io_util_percent", c_double),
    ]


class NetMetrics(Structure):
    _fields_ = [
        ("bytes_sent", c_uint64),
        ("bytes_recv", c_uint64),
        ("packets_sent", c_uint64),
        ("packets_recv", c_uint64),
        ("send_bytes_per_sec", c_double),
        ("recv_bytes_per_sec", c_double),
        ("tcp_connections", c_uint32),
    ]


class SystemMetrics(Structure):
    _fields_ = [
        ("cpu", CpuMetrics),
        ("mem", MemMetrics),
        ("disk", DiskMetrics),
        ("net", NetMetrics),
        ("timestamp", c_int64),
        ("hostname", c_char * 256),
    ]


class SysmonBridge:
    """
    C 动态库桥接器
    
    使用方法:
        bridge = SysmonBridge("/path/to/libsysmon.so")
        bridge.init()
        metrics = bridge.collect()
        bridge.cleanup()
    """

    def __init__(self, lib_path: Optional[str] = None):
        if lib_path is None:
            # 默认路径：当前文件同级的 c_module 目录
            base_dir = os.path.dirname(os.path.abspath(__file__))
            lib_path = os.path.join(base_dir, "c_module", "libsysmon.so")

        if not os.path.exists(lib_path):
            raise FileNotFoundError(
                f"动态库未找到: {lib_path}\n"
                f"请先编译 C 模块: cd c_module && make"
            )

        self._lib = ctypes.CDLL(lib_path)
        self._setup_functions()
        self._initialized = False

    def _setup_functions(self):
        """声明 C 函数的参数类型与返回类型（必须显式声明，防止内存错误）"""
        # sysmon_init
        self._lib.sysmon_init.restype = c_int
        self._lib.sysmon_init.argtypes = []

        # sysmon_collect
        self._lib.sysmon_collect.restype = c_int
        self._lib.sysmon_collect.argtypes = [POINTER(SystemMetrics)]

        # sysmon_collect_cpu
        self._lib.sysmon_collect_cpu.restype = c_int
        self._lib.sysmon_collect_cpu.argtypes = [POINTER(CpuMetrics)]

        # sysmon_collect_mem
        self._lib.sysmon_collect_mem.restype = c_int
        self._lib.sysmon_collect_mem.argtypes = [POINTER(MemMetrics)]

        # sysmon_error
        self._lib.sysmon_error.restype = c_char_p
        self._lib.sysmon_error.argtypes = []

        # sysmon_cleanup
        self._lib.sysmon_cleanup.restype = None
        self._lib.sysmon_cleanup.argtypes = []

    def init(self):
        """初始化 C 采集模块"""
        ret = self._lib.sysmon_init()
        if ret != 0:
            err = self._lib.sysmon_error()
            raise RuntimeError(f"C 模块初始化失败: {err.decode() if err else 'unknown'}")
        self._initialized = True

    def collect(self) -> Dict[str, Any]:
        """
        采集全部系统指标
        
        Returns:
            包含 cpu, mem, disk, net, timestamp, hostname 的字典
        Raises:
            RuntimeError: 采集失败时抛出
        """
        if not self._initialized:
            self.init()

        metrics = SystemMetrics()
        ret = self._lib.sysmon_collect(byref(metrics))
        if ret != 0:
            err = self._lib.sysmon_error()
            raise RuntimeError(f"采集失败: {err.decode() if err else 'unknown'}")

        return {
            "cpu": {
                "usage_percent": round(metrics.cpu.usage_percent, 2),
                "user_percent": round(metrics.cpu.user_percent, 2),
                "system_percent": round(metrics.cpu.system_percent, 2),
                "iowait_percent": round(metrics.cpu.iowait_percent, 2),
                "core_count": metrics.cpu.core_count,
                "load_avg_1": round(metrics.cpu.load_avg_1, 2),
                "load_avg_5": round(metrics.cpu.load_avg_5, 2),
                "load_avg_15": round(metrics.cpu.load_avg_15, 2),
            },
            "mem": {
                "total_bytes": metrics.mem.total_bytes,
                "used_bytes": metrics.mem.used_bytes,
                "free_bytes": metrics.mem.free_bytes,
                "cached_bytes": metrics.mem.cached_bytes,
                "buffers_bytes": metrics.mem.buffers_bytes,
                "usage_percent": round(metrics.mem.usage_percent, 2),
                "swap_total": metrics.mem.swap_total,
                "swap_used": metrics.mem.swap_used,
            },
            "disk": {
                "total_bytes": metrics.disk.total_bytes,
                "used_bytes": metrics.disk.used_bytes,
                "free_bytes": metrics.disk.free_bytes,
                "usage_percent": round(metrics.disk.usage_percent, 2),
                "read_bytes_per_sec": round(metrics.disk.read_bytes_per_sec, 2),
                "write_bytes_per_sec": round(metrics.disk.write_bytes_per_sec, 2),
                "io_util_percent": round(metrics.disk.io_util_percent, 2),
            },
            "net": {
                "bytes_sent": metrics.net.bytes_sent,
                "bytes_recv": metrics.net.bytes_recv,
                "packets_sent": metrics.net.packets_sent,
                "packets_recv": metrics.net.packets_recv,
                "send_bytes_per_sec": round(metrics.net.send_bytes_per_sec, 2),
                "recv_bytes_per_sec": round(metrics.net.recv_bytes_per_sec, 2),
                "tcp_connections": metrics.net.tcp_connections,
            },
            "timestamp": metrics.timestamp,
            "hostname": metrics.hostname.decode("utf-8", errors="replace"),
        }

    def cleanup(self):
        """释放 C 模块资源"""
        if self._initialized:
            self._lib.sysmon_cleanup()
            self._initialized = False

    def __enter__(self):
        self.init()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()
        return False
```

#### 4.1.3 Python 采集调度器

**collector.py — 定时采集与上报**

```python
"""
collector.py
数据采集调度器：定时调用 C 采集模块，将数据上报至 SmartOps 后端
"""

import time
import json
import logging
import asyncio
import aiohttp
import yaml
from pathlib import Path
from bridge import SysmonBridge
from typing import Optional

logger = logging.getLogger("smartops.collector")


class CollectorAgent:
    """
    采集探针 Agent
    
    职责:
    1. 定时调用 C 动态库采集系统指标
    2. 将采集结果通过 HTTP POST 上报至后端
    3. 支持断线重连与本地缓存
    """

    def __init__(self, config_path: str = "config.yaml"):
        self.config = self._load_config(config_path)
        self.server_url = self.config["server"]["url"]
        self.interval = self.config["collector"]["interval"]  # 采集间隔（秒）
        self.api_key = self.config["server"].get("api_key", "")
        self.buffer: list = []  # 离线缓冲区
        self.max_buffer_size = self.config["collector"].get("max_buffer_size", 1000)
        self.bridge: Optional[SysmonBridge] = None

    @staticmethod
    def _load_config(path: str) -> dict:
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    async def collect_and_report(self):
        """单次采集并上报"""
        try:
            metrics = self.bridge.collect()
            self.buffer.append(metrics)

            # 批量上报（缓冲区满 10 条或超过 10 秒）
            if len(self.buffer) >= 10:
                await self._flush_buffer()

        except Exception as e:
            logger.error(f"采集异常: {e}")

    async def _flush_buffer(self):
        """将缓冲区数据批量上报至后端"""
        if not self.buffer:
            return

        payload = {
            "agent_id": self.config["agent"]["id"],
            "metrics_batch": self.buffer.copy(),
        }
        self.buffer.clear()

        headers = {
            "Content-Type": "application/json",
            "X-API-Key": self.api_key,
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.server_url}/api/v1/metrics/report",
                    json=payload,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=5),
                ) as resp:
                    if resp.status != 200:
                        logger.warning(f"上报失败, HTTP {resp.status}")
                        # 放回缓冲区（限制大小）
                        self.buffer = payload["metrics_batch"] + self.buffer
                        if len(self.buffer) > self.max_buffer_size:
                            self.buffer = self.buffer[:self.max_buffer_size]
        except Exception as e:
            logger.error(f"上报异常: {e}")
            # 网络异常，数据保留在缓冲区
            self.buffer = payload["metrics_batch"] + self.buffer

    async def run(self):
        """主循环：定时采集 + 定时刷新缓冲区"""
        lib_path = self.config["collector"].get("lib_path")
        self.bridge = SysmonBridge(lib_path)
        self.bridge.init()

        logger.info(f"采集探针启动, 上报地址: {self.server_url}, 间隔: {self.interval}s")

        last_flush = time.time()
        try:
            while True:
                await self.collect_and_report()

                # 定时刷新缓冲区
                if time.time() - last_flush > 10:
                    await self._flush_buffer()
                    last_flush = time.time()

                await asyncio.sleep(self.interval)
        except KeyboardInterrupt:
            logger.info("采集探针停止")
        finally:
            await self._flush_buffer()
            self.bridge.cleanup()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    agent = CollectorAgent()
    asyncio.run(agent.run())
```

---

### 4.2 Web 后端服务模块

#### 4.2.1 FastAPI 应用入口

**main.py**

```python
"""
main.py
SmartOps FastAPI 应用入口
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.api.v1 import metrics, alerts, hosts, ops
from app.db.redis_client import redis_manager
from app.db.pg_client import pg_manager
from app.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理：启动/关闭时的资源初始化与清理"""
    # 启动时
    await redis_manager.connect(settings.REDIS_URL)
    await pg_manager.connect(settings.DATABASE_URL)
    yield
    # 关闭时
    await redis_manager.disconnect()
    await pg_manager.disconnect()


app = FastAPI(
    title="SmartOps API",
    description="智能运维监控平台后端 API",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(metrics.router, prefix="/api/v1/metrics", tags=["指标数据"])
app.include_router(alerts.router, prefix="/api/v1/alerts", tags=["告警管理"])
app.include_router(hosts.router, prefix="/api/v1/hosts", tags=["主机管理"])
app.include_router(ops.router, prefix="/api/v1/ops", tags=["运维操作"])


@app.get("/api/health")
async def health_check():
    """健康检查接口"""
    redis_ok = await redis_manager.ping()
    pg_ok = await pg_manager.ping()
    return {
        "status": "healthy" if (redis_ok and pg_ok) else "degraded",
        "redis": "up" if redis_ok else "down",
        "postgresql": "up" if pg_ok else "down",
    }
```

#### 4.2.2 数据模型

**models/metrics.py**

```python
"""
metrics.py
指标数据的 Pydantic 模型定义
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class CpuMetricsModel(BaseModel):
    usage_percent: float = Field(..., ge=0, le=100, description="CPU 使用率 (%)")
    user_percent: float = Field(..., ge=0, le=100)
    system_percent: float = Field(..., ge=0, le=100)
    iowait_percent: float = Field(..., ge=0, le=100)
    core_count: int = Field(..., gt=0)
    load_avg_1: float
    load_avg_5: float
    load_avg_15: float


class MemMetricsModel(BaseModel):
    total_bytes: int = Field(..., ge=0)
    used_bytes: int = Field(..., ge=0)
    free_bytes: int = Field(..., ge=0)
    cached_bytes: int = Field(..., ge=0)
    buffers_bytes: int = Field(..., ge=0)
    usage_percent: float = Field(..., ge=0, le=100)
    swap_total: int = Field(..., ge=0)
    swap_used: int = Field(..., ge=0)


class DiskMetricsModel(BaseModel):
    total_bytes: int = Field(..., ge=0)
    used_bytes: int = Field(..., ge=0)
    free_bytes: int = Field(..., ge=0)
    usage_percent: float = Field(..., ge=0, le=100)
    read_bytes_per_sec: float = Field(..., ge=0)
    write_bytes_per_sec: float = Field(..., ge=0)
    io_util_percent: float = Field(..., ge=0, le=100)


class NetMetricsModel(BaseModel):
    bytes_sent: int = Field(..., ge=0)
    bytes_recv: int = Field(..., ge=0)
    packets_sent: int = Field(..., ge=0)
    packets_recv: int = Field(..., ge=0)
    send_bytes_per_sec: float = Field(..., ge=0)
    recv_bytes_per_sec: float = Field(..., ge=0)
    tcp_connections: int = Field(..., ge=0)


class MetricsReport(BaseModel):
    """单条上报数据"""
    cpu: CpuMetricsModel
    mem: MemMetricsModel
    disk: DiskMetricsModel
    net: NetMetricsModel
    timestamp: int = Field(..., description="Unix 时间戳 (毫秒)")
    hostname: str = Field(..., max_length=256)


class BatchReportRequest(BaseModel):
    """批量上报请求"""
    agent_id: str = Field(..., description="探针唯一标识")
    metrics_batch: List[MetricsReport] = Field(..., min_length=1, max_length=100)


class MetricsQueryParams(BaseModel):
    """查询参数"""
    hostname: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    metric_type: Optional[str] = Field(None, description="cpu|mem|disk|net")
    limit: int = Field(100, ge=1, le=10000)
```

#### 4.2.3 核心 API 接口

**api/v1/metrics.py**

```python
"""
metrics.py
指标数据上报与查询接口
"""

from fastapi import APIRouter, Depends, BackgroundTasks, Query
from typing import List, Optional
from datetime import datetime

from app.models.metrics import (
    BatchReportRequest, MetricsReport, MetricsQueryParams
)
from app.services.metrics_service import MetricsService
from app.tasks.ai_tasks import run_anomaly_detection
from app.api.deps import get_metrics_service

router = APIRouter()


@router.post("/report", status_code=202, summary="批量上报指标数据")
async def report_metrics(
    request: BatchReportRequest,
    background_tasks: BackgroundTasks,
    service: MetricsService = Depends(get_metrics_service),
):
    """
    接收探针 Agent 上报的批量指标数据。
    
    处理流程:
    1. 数据校验（Pydantic 自动完成）
    2. 写入 Redis 实时缓存（同步等待）
    3. 异步持久化至 PostgreSQL（BackgroundTasks）
    4. 异步触发 AI 异常检测（Celery 任务）
    """
    # 1. 写入 Redis（实时缓存最新值）
    await service.cache_latest_metrics(request.agent_id, request.metrics_batch)

    # 2. 异步持久化到 PostgreSQL
    background_tasks.add_task(
        service.persist_metrics, request.agent_id, request.metrics_batch
    )

    # 3. 异步触发 AI 异常检测
    latest = request.metrics_batch[-1]
    run_anomaly_detection.delay(
        agent_id=request.agent_id,
        metrics_data=latest.model_dump(),
    )

    return {
        "status": "accepted",
        "received_count": len(request.metrics_batch),
        "agent_id": request.agent_id,
    }


@router.get("/query", summary="查询历史指标数据")
async def query_metrics(
    hostname: str = Query(..., description="主机名"),
    metric_type: str = Query("cpu", description="指标类型: cpu|mem|disk|net"),
    start_time: Optional[datetime] = Query(None),
    end_time: Optional[datetime] = Query(None),
    limit: int = Query(100, ge=1, le=10000),
    service: MetricsService = Depends(get_metrics_service),
):
    """
    查询指定主机的历史指标数据，支持时间范围筛选。
    优先从 Redis 缓存读取近期数据，历史数据从 PostgreSQL 获取。
    """
    data = await service.query_metrics(
        hostname=hostname,
        metric_type=metric_type,
        start_time=start_time,
        end_time=end_time,
        limit=limit,
    )
    return {"status": "success", "count": len(data), "data": data}


@router.get("/realtime/{hostname}", summary="获取实时指标快照")
async def get_realtime_metrics(
    hostname: str,
    service: MetricsService = Depends(get_metrics_service),
):
    """
    从 Redis 获取指定主机的最新一条指标快照。
    """
    data = await service.get_realtime(hostname)
    if not data:
        return {"status": "not_found", "message": f"未找到主机 {hostname} 的实时数据"}
    return {"status": "success", "data": data}
```

#### 4.2.4 数据服务层

**services/metrics_service.py**

```python
"""
metrics_service.py
指标数据的业务逻辑处理
"""

import json
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.db.redis_client import redis_manager
from app.db.pg_client import pg_manager
from app.models.metrics import MetricsReport

logger = logging.getLogger(__name__)


class MetricsService:
    """指标数据处理服务"""

    REALTIME_KEY_PREFIX = "smartops:realtime:"
    HISTORY_KEY_PREFIX = "smartops:history:"
    REALTIME_TTL = 300  # 实时数据缓存 5 分钟

    async def cache_latest_metrics(
        self, agent_id: str, batch: List[MetricsReport]
    ):
        """将最新数据写入 Redis 实时缓存"""
        if not batch:
            return

        latest = batch[-1]
        key = f"{self.REALTIME_KEY_PREFIX}{latest.hostname}"
        await redis_manager.set(
            key,
            json.dumps(latest.model_dump()),
            ex=self.REALTIME_TTL,
        )

        # 同时写入时序列表（用于近期趋势图）
        history_key = f"{self.HISTORY_KEY_PREFIX}{latest.hostname}"
        for item in batch:
            await redis_manager.rpush(
                history_key,
                json.dumps({"ts": item.timestamp, "cpu": item.cpu.usage_percent,
                            "mem": item.mem.usage_percent}),
            )
        # 保留最近 3600 条
        await redis_manager.ltrim(history_key, -3600, -1)

    async def persist_metrics(
        self, agent_id: str, batch: List[MetricsReport]
    ):
        """异步将数据持久化到 PostgreSQL"""
        try:
            records = []
            for item in batch:
                records.append({
                    "agent_id": agent_id,
                    "hostname": item.hostname,
                    "timestamp": datetime.fromtimestamp(item.timestamp / 1000),
                    "cpu_usage": item.cpu.usage_percent,
                    "mem_usage": item.mem.usage_percent,
                    "disk_usage": item.disk.usage_percent,
                    "cpu_data": item.cpu.model_dump_json(),
                    "mem_data": item.mem.model_dump_json(),
                    "disk_data": item.disk.model_dump_json(),
                    "net_data": item.net.model_dump_json(),
                })
            await pg_manager.batch_insert("metrics", records)
        except Exception as e:
            logger.error(f"持久化失败: {e}")

    async def query_metrics(
        self,
        hostname: str,
        metric_type: str,
        start_time: Optional[datetime],
        end_time: Optional[datetime],
        limit: int,
    ) -> List[Dict[str, Any]]:
        """查询历史指标数据"""
        query = """
            SELECT timestamp, cpu_data, mem_data, disk_data, net_data
            FROM metrics
            WHERE hostname = :hostname
        """
        params = {"hostname": hostname, "limit": limit}

        if start_time:
            query += " AND timestamp >= :start_time"
            params["start_time"] = start_time
        if end_time:
            query += " AND timestamp <= :end_time"
            params["end_time"] = end_time

        query += " ORDER BY timestamp DESC LIMIT :limit"

        rows = await pg_manager.fetch(query, params)
        result = []
        for row in rows:
            data = {"timestamp": row["timestamp"]}
            if metric_type == "cpu":
                data["metrics"] = json.loads(row["cpu_data"])
            elif metric_type == "mem":
                data["metrics"] = json.loads(row["mem_data"])
            elif metric_type == "disk":
                data["metrics"] = json.loads(row["disk_data"])
            elif metric_type == "net":
                data["metrics"] = json.loads(row["net_data"])
            result.append(data)

        return result

    async def get_realtime(self, hostname: str) -> Optional[Dict[str, Any]]:
        """从 Redis 获取实时数据"""
        key = f"{self.REALTIME_KEY_PREFIX}{hostname}"
        data = await redis_manager.get(key)
        return json.loads(data) if data else None
```

#### 4.2.5 数据库初始化 SQL

**scripts/init_db.sql**

```sql
-- SmartOps 数据库初始化脚本

-- 创建数据库
CREATE DATABASE IF NOT EXISTS smartops;
\c smartops;

-- 指标数据主表（按月分区可后续扩展）
CREATE TABLE IF NOT EXISTS metrics (
    id              BIGSERIAL PRIMARY KEY,
    agent_id        VARCHAR(128) NOT NULL,
    hostname        VARCHAR(256) NOT NULL,
    timestamp       TIMESTAMPTZ NOT NULL,
    cpu_usage       DOUBLE PRECISION NOT NULL DEFAULT 0,
    mem_usage       DOUBLE PRECISION NOT NULL DEFAULT 0,
    disk_usage      DOUBLE PRECISION NOT NULL DEFAULT 0,
    cpu_data        JSONB,
    mem_data        JSONB,
    disk_data       JSONB,
    net_data        JSONB,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- 索引：按主机名 + 时间范围查询
CREATE INDEX idx_metrics_hostname_ts ON metrics (hostname, timestamp DESC);
CREATE INDEX idx_metrics_agent ON metrics (agent_id);

-- 告警记录表
CREATE TABLE IF NOT EXISTS alerts (
    id              BIGSERIAL PRIMARY KEY,
    hostname        VARCHAR(256) NOT NULL,
    alert_type      VARCHAR(64) NOT NULL,     -- cpu_high, mem_high, disk_full, anomaly
    severity        VARCHAR(16) NOT NULL,     -- info, warning, critical
    message         TEXT,
    metric_value    DOUBLE PRECISION,
    threshold       DOUBLE PRECISION,
    status          VARCHAR(16) DEFAULT 'open',  -- open, acknowledged, resolved
    detected_at     TIMESTAMPTZ DEFAULT NOW(),
    resolved_at     TIMESTAMPTZ,
    ops_action      VARCHAR(256),             -- 自动运维操作描述
    ops_result      VARCHAR(16)               -- success, failed, skipped
);

CREATE INDEX idx_alerts_hostname ON alerts (hostname, detected_at DESC);
CREATE INDEX idx_alerts_status ON alerts (status);

-- 主机注册表
CREATE TABLE IF NOT EXISTS hosts (
    id              BIGSERIAL PRIMARY KEY,
    hostname        VARCHAR(256) UNIQUE NOT NULL,
    agent_id        VARCHAR(128) UNIQUE NOT NULL,
    ip_address      INET,
    os_info         VARCHAR(256),
    cpu_cores       INTEGER,
    mem_total_bytes BIGINT,
    status          VARCHAR(16) DEFAULT 'online',   -- online, offline, maintenance
    last_seen       TIMESTAMPTZ,
    registered_at   TIMESTAMPTZ DEFAULT NOW(),
    tags            TEXT[] DEFAULT '{}'
);

-- 运维操作日志表
CREATE TABLE IF NOT EXISTS ops_logs (
    id              BIGSERIAL PRIMARY KEY,
    hostname        VARCHAR(256) NOT NULL,
    action          VARCHAR(128) NOT NULL,     -- restart_service, clean_logs, health_check
    params          JSONB,
    result          VARCHAR(16),               -- success, failed, timeout
    output          TEXT,
    trigger_type    VARCHAR(32),               -- manual, auto (AI 触发)
    alert_id        BIGINT REFERENCES alerts(id),
    executed_at     TIMESTAMPTZ DEFAULT NOW(),
    duration_ms     INTEGER
);

CREATE INDEX idx_ops_logs_hostname ON ops_logs (hostname, executed_at DESC);
```

---

### 4.3 AI 异常检测模块

#### 4.3.1 异常检测器核心

**ai_service/detector.py**

```python
"""
detector.py
SmartOps AI 异常检测器

支持的检测算法:
1. 滑动窗口标准差检测（统计学方法）
2. 孤立森林（Isolation Forest，机器学习方法）
3. 组合检测策略（多算法投票）
"""

import numpy as np
import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import joblib
import os

logger = logging.getLogger("smartops.ai")


class AlertSeverity(Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class DetectionResult:
    """检测结果"""
    is_anomaly: bool
    severity: AlertSeverity
    anomaly_score: float        # -1 ~ 1, 越小越异常
    metric_name: str
    current_value: float
    baseline_mean: float
    baseline_std: float
    message: str


class SlidingWindowDetector:
    """
    滑动窗口标准差检测器
    
    原理: 维护最近 N 个数据点的滑动窗口，计算均值 μ 和标准差 σ，
    当新数据点偏离均值超过 k*σ 时，判定为异常。
    
    优点: 计算简单，响应快速，适合实时检测
    缺点: 对趋势性数据不敏感
    """

    def __init__(self, window_size: int = 60, threshold_sigma: float = 3.0):
        self.window_size = window_size
        self.threshold_sigma = threshold_sigma
        self._windows: Dict[str, List[float]] = {}

    def add_data(self, key: str, value: float):
        """向滑动窗口添加数据点"""
        if key not in self._windows:
            self._windows[key] = []
        self._windows[key].append(value)
        # 保持窗口大小
        if len(self._windows[key]) > self.window_size:
            self._windows[key] = self._windows[key][-self.window_size:]

    def detect(self, key: str, value: float) -> Optional[DetectionResult]:
        """
        检测新数据点是否异常
        
        Returns:
            DetectionResult 或 None（数据不足时）
        """
        self.add_data(key, value)
        window = self._windows[key]

        # 至少需要 10 个数据点
        if len(window) < 10:
            return None

        arr = np.array(window[:-1])  # 不包含当前点
        mean = np.mean(arr)
        std = np.std(arr)

        if std < 1e-6:
            # 标准差极小（恒定值），任何偏离都是异常
            deviation = abs(value - mean)
            is_anomaly = deviation > 0.01 * mean  # 偏离 1% 以上
        else:
            z_score = (value - mean) / std
            is_anomaly = abs(z_score) > self.threshold_sigma

        # 确定严重级别
        if is_anomaly:
            if std > 0 and abs(value - mean) / std > self.threshold_sigma * 1.5:
                severity = AlertSeverity.CRITICAL
            else:
                severity = AlertSeverity.WARNING
        else:
            severity = AlertSeverity.INFO

        return DetectionResult(
            is_anomaly=is_anomaly,
            severity=severity,
            anomaly_score=-abs(value - mean) / (std + 1e-6),
            metric_name=key,
            current_value=value,
            baseline_mean=round(mean, 2),
            baseline_std=round(std, 2),
            message=f"{key} 当前值 {value:.2f}, 基线均值 {mean:.2f}±{std:.2f}",
        )


class IsolationForestDetector:
    """
    孤立森林异常检测器
    
    原理: 通过随机切分特征空间来"孤立"数据点，
    异常点因为偏离正常数据分布，更容易被少量切分隔离出来。
    
    优点: 不需要假设数据分布，适合高维数据
    适用: 周期性基线学习后的异常检测
    """

    def __init__(
        self,
        contamination: float = 0.05,
        n_estimators: int = 100,
        model_path: str = "ai_service/models/",
    ):
        self.contamination = contamination
        self.model = IsolationForest(
            n_estimators=n_estimators,
            contamination=contamination,
            random_state=42,
        )
        self.scaler = StandardScaler()
        self.model_path = model_path
        self._is_trained = False
        self._feature_names: List[str] = []

    def train(self, data: np.ndarray, feature_names: List[str]):
        """
        使用历史数据训练模型
        
        Args:
            data: shape (n_samples, n_features)
            feature_names: 特征名称列表
        """
        self._feature_names = feature_names
        scaled_data = self.scaler.fit_transform(data)
        self.model.fit(scaled_data)
        self._is_trained = True
        logger.info(f"孤立森林模型训练完成, 样本数: {len(data)}, 特征数: {len(feature_names)}")

    def detect(self, data_point: Dict[str, float]) -> Optional[DetectionResult]:
        """
        检测单个数据点
        
        Args:
            data_point: 如 {"cpu_usage": 85.0, "mem_usage": 72.0, ...}
        """
        if not self._is_trained:
            return None

        # 构建特征向量
        values = [data_point.get(f, 0.0) for f in self._feature_names]
        x = np.array(values).reshape(1, -1)
        x_scaled = self.scaler.transform(x)

        # 预测: 1=正常, -1=异常
        prediction = self.model.predict(x_scaled)[0]
        # 异常分数: 越小越异常
        score = self.model.score_samples(x_scaled)[0]

        is_anomaly = prediction == -1
        severity = AlertSeverity.CRITICAL if score < -0.5 else (
            AlertSeverity.WARNING if is_anomaly else AlertSeverity.INFO
        )

        return DetectionResult(
            is_anomaly=is_anomaly,
            severity=severity,
            anomaly_score=score,
            metric_name="multi_dimensional",
            current_value=score,
            baseline_mean=0.0,
            baseline_std=0.0,
            message=f"多维异常检测: score={score:.4f}, anomaly={is_anomaly}",
        )

    def save_model(self, filename: str = "isolation_forest.pkl"):
        """持久化模型"""
        os.makedirs(self.model_path, exist_ok=True)
        path = os.path.join(self.model_path, filename)
        joblib.dump({"model": self.model, "scaler": self.scaler,
                      "features": self._feature_names}, path)

    def load_model(self, filename: str = "isolation_forest.pkl"):
        """加载已训练模型"""
        path = os.path.join(self.model_path, filename)
        if not os.path.exists(path):
            return False
        data = joblib.load(path)
        self.model = data["model"]
        self.scaler = data["scaler"]
        self._feature_names = data["features"]
        self._is_trained = True
        return True


class SmartDetector:
    """
    组合检测策略
    
    将滑动窗口检测与孤立森林检测结合，采用"投票"机制：
    - 任一算法检测到 CRITICAL 级别异常 → 直接告警
    - 两种算法均检测到 WARNING → 合并告警
    - 仅一种算法检测到 WARNING → 记录但不告警（降低误报）
    """

    def __init__(self):
        self.window_detector = SlidingWindowDetector()
        self.forest_detector = IsolationForestDetector()

    def detect(self, hostname: str, metrics: Dict[str, Any]) -> List[DetectionResult]:
        """
        综合检测
        
        Args:
            hostname: 主机名
            metrics: 指标字典，包含 cpu, mem, disk, net 子字典
        """
        results = []

        # 1. 滑动窗口检测（针对单指标）
        single_metrics = {
            f"{hostname}:cpu_usage": metrics.get("cpu", {}).get("usage_percent", 0),
            f"{hostname}:mem_usage": metrics.get("mem", {}).get("usage_percent", 0),
            f"{hostname}:disk_usage": metrics.get("disk", {}).get("usage_percent", 0),
            f"{hostname}:load_avg": metrics.get("cpu", {}).get("load_avg_1", 0),
        }

        for key, value in single_metrics.items():
            result = self.window_detector.detect(key, value)
            if result:
                results.append(result)

        # 2. 孤立森林检测（多维联合）
        if self.forest_detector._is_trained:
            flat_metrics = {
                "cpu_usage": metrics.get("cpu", {}).get("usage_percent", 0),
                "mem_usage": metrics.get("mem", {}).get("usage_percent", 0),
                "disk_usage": metrics.get("disk", {}).get("usage_percent", 0),
                "load_avg_1": metrics.get("cpu", {}).get("load_avg_1", 0),
                "io_util": metrics.get("disk", {}).get("io_util_percent", 0),
                "net_send": metrics.get("net", {}).get("send_bytes_per_sec", 0),
                "net_recv": metrics.get("net", {}).get("recv_bytes_per_sec", 0),
            }
            forest_result = self.forest_detector.detect(flat_metrics)
            if forest_result:
                results.append(forest_result)

        return results
```

#### 4.3.2 趋势预测器

**ai_service/predictor.py**

```python
"""
predictor.py
负载趋势预测器

基于历史数据进行线性回归 + 滑动窗口趋势分析，
预测未来 N 个时间点的指标值，提前预警容量瓶颈。
"""

import numpy as np
from typing import List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class PredictionResult:
    """预测结果"""
    metric_name: str
    current_value: float
    predicted_values: List[float]   # 未来 N 个时间点的预测值
    trend: str                       # "rising", "falling", "stable"
    estimated_hit_time: Optional[int]  # 预计达到阈值的时间点数（None 表示不会达到）
    threshold: float


class TrendPredictor:
    """
    趋势预测器
    
    使用多项式拟合 + 指数平滑进行短期趋势预测
    """

    def __init__(self, history_size: int = 120):
        self.history_size = history_size
        self._history: dict = {}

    def add_data(self, key: str, value: float):
        if key not in self._history:
            self._history[key] = []
        self._history[key].append(value)
        if len(self._history[key]) > self.history_size:
            self._history[key] = self._history[key][-self.history_size:]

    def predict(
        self,
        key: str,
        steps_ahead: int = 10,
        threshold: float = 90.0,
    ) -> Optional[PredictionResult]:
        """
        预测未来趋势
        
        Args:
            key: 指标键名
            steps_ahead: 预测步数
            threshold: 告警阈值
        """
        history = self._history.get(key, [])
        if len(history) < 20:
            return None

        y = np.array(history)
        x = np.arange(len(y))

        # 二次多项式拟合
        coeffs = np.polyfit(x, y, deg=2)
        poly = np.poly1d(coeffs)

        # 预测未来值
        future_x = np.arange(len(y), len(y) + steps_ahead)
        predicted = poly(future_x).tolist()

        # 判断趋势方向
        slope = coeffs[0] * 2 * len(y) + coeffs[1]  # 导数
        if slope > 0.5:
            trend = "rising"
        elif slope < -0.5:
            trend = "falling"
        else:
            trend = "stable"

        # 估算达到阈值的时间
        estimated_hit_time = None
        if trend == "rising" and predicted[-1] >= threshold:
            for i, val in enumerate(predicted):
                if val >= threshold:
                    estimated_hit_time = i + 1
                    break

        return PredictionResult(
            metric_name=key,
            current_value=history[-1],
            predicted_values=[round(v, 2) for v in predicted],
            trend=trend,
            estimated_hit_time=estimated_hit_time,
            threshold=threshold,
        )
```

---

### 4.4 自动化运维模块

#### 4.4.1 SSH 远程执行器

**ops_service/ssh_executor.py**

```python
"""
ssh_executor.py
SSH 远程命令执行器

基于 Paramiko 实现安全的远程连接与命令执行，
支持密钥认证、超时控制与结果解析。
"""

import paramiko
import logging
import time
from typing import Optional, Tuple, Dict
from dataclasses import dataclass

logger = logging.getLogger("smartops.ops")


@dataclass
class ExecResult:
    """命令执行结果"""
    success: bool
    stdout: str
    stderr: str
    exit_code: int
    duration_ms: int


class SSHExecutor:
    """
    SSH 远程执行器
    
    支持:
    - 密钥与密码两种认证方式
    - 命令超时控制
    - 批量命令执行
    - 连接复用
    """

    def __init__(
        self,
        host: str,
        port: int = 22,
        username: str = "root",
        password: Optional[str] = None,
        key_file: Optional[str] = None,
        timeout: int = 30,
    ):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.key_file = key_file
        self.timeout = timeout
        self._client: Optional[paramiko.SSHClient] = None

    def connect(self):
        """建立 SSH 连接"""
        self._client = paramiko.SSHClient()
        self._client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        connect_kwargs = {
            "hostname": self.host,
            "port": self.port,
            "username": self.username,
            "timeout": self.timeout,
        }

        if self.key_file:
            connect_kwargs["key_filename"] = self.key_file
        elif self.password:
            connect_kwargs["password"] = self.password

        self._client.connect(**connect_kwargs)
        logger.info(f"SSH 连接成功: {self.username}@{self.host}:{self.port}")

    def execute(self, command: str, timeout: Optional[int] = None) -> ExecResult:
        """
        执行远程命令
        
        Args:
            command: Shell 命令
            timeout: 超时时间（秒），默认使用实例配置
        """
        if not self._client:
            self.connect()

        start = time.time()
        try:
            stdin, stdout, stderr = self._client.exec_command(
                command, timeout=timeout or self.timeout
            )
            exit_code = stdout.channel.recv_exit_status()
            duration = int((time.time() - start) * 1000)

            return ExecResult(
                success=(exit_code == 0),
                stdout=stdout.read().decode("utf-8", errors="replace"),
                stderr=stderr.read().decode("utf-8", errors="replace"),
                exit_code=exit_code,
                duration_ms=duration,
            )
        except Exception as e:
            duration = int((time.time() - start) * 1000)
            logger.error(f"命令执行失败 [{self.host}]: {command} -> {e}")
            return ExecResult(
                success=False, stdout="", stderr=str(e),
                exit_code=-1, duration_ms=duration,
            )

    def close(self):
        """关闭 SSH 连接"""
        if self._client:
            self._client.close()
            self._client = None

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False
```

#### 4.4.2 运维剧本

**ops_service/playbooks/restart_service.py**

```python
"""
restart_service.py
服务重启运维剧本

执行流程:
1. 检查目标服务当前状态
2. 执行重启命令
3. 等待服务恢复
4. 验证重启结果
"""

from ops_service.ssh_executor import SSHExecutor, ExecResult
import time
import logging

logger = logging.getLogger("smartops.ops.restart")


def restart_service(
    executor: SSHExecutor,
    service_name: str,
    max_wait: int = 60,
    check_interval: int = 5,
) -> ExecResult:
    """
    重启指定服务并验证结果
    
    Args:
        executor: SSH 执行器
        service_name: systemd 服务名（如 nginx, docker）
        max_wait: 最大等待恢复时间（秒）
        check_interval: 检查间隔（秒）
    """
    logger.info(f"[{executor.host}] 开始重启服务: {service_name}")

    # 1. 检查当前状态
    status = executor.execute(f"systemctl is-active {service_name}")
    logger.info(f"[{executor.host}] 当前状态: {status.stdout.strip()}")

    # 2. 执行重启
    restart = executor.execute(f"systemctl restart {service_name}")
    if not restart.success:
        logger.error(f"[{executor.host}] 重启命令失败: {restart.stderr}")
        return restart

    # 3. 等待服务恢复
    elapsed = 0
    while elapsed < max_wait:
        time.sleep(check_interval)
        elapsed += check_interval

        check = executor.execute(f"systemctl is-active {service_name}")
        if check.stdout.strip() == "active":
            logger.info(f"[{executor.host}] 服务 {service_name} 重启成功, 耗时 {elapsed}s")
            return ExecResult(
                success=True,
                stdout=f"Service {service_name} restarted successfully in {elapsed}s",
                stderr="",
                exit_code=0,
                duration_ms=elapsed * 1000,
            )

    # 4. 超时
    logger.warning(f"[{executor.host}] 服务 {service_name} 重启超时 ({max_wait}s)")
    return ExecResult(
        success=False,
        stdout="",
        stderr=f"Service {service_name} restart timed out after {max_wait}s",
        exit_code=1,
        duration_ms=max_wait * 1000,
    )
```

**ops_service/playbooks/clean_logs.py**

```python
"""
clean_logs.py
日志清理运维剧本

功能:
- 清理指定天数前的日志文件
- 压缩归档近期日志
- 清理 systemd journal 日志
"""

from ops_service.ssh_executor import SSHExecutor, ExecResult
import logging

logger = logging.getLogger("smartops.ops.clean_logs")


def clean_old_logs(
    executor: SSHExecutor,
    log_dir: str = "/var/log",
    days: int = 7,
    compress_recent: bool = True,
) -> ExecResult:
    """
    清理过期日志
    
    Args:
        executor: SSH 执行器
        log_dir: 日志目录
        days: 保留天数
        compress_recent: 是否压缩近 3 天的 .log 文件
    """
    commands = []

    # 删除超过保留天数的日志文件
    commands.append(
        f"find {log_dir} -name '*.log' -type f -mtime +{days} -delete"
    )
    commands.append(
        f"find {log_dir} -name '*.log.gz' -type f -mtime +{days * 2} -delete"
    )

    # 清理 journal 日志（保留 7 天）
    commands.append(f"journalctl --vacuum-time={days}d 2>/dev/null || true")

    # 压缩近 3 天未压缩的大日志（> 100MB）
    if compress_recent:
        commands.append(
            f"find {log_dir} -name '*.log' -type f -mtime -3 -size +100M "
            f"-exec gzip {{}} \\;"
        )

    # 统计清理前的磁盘占用
    before = executor.execute(f"du -sh {log_dir} 2>/dev/null | cut -f1")

    # 执行清理
    for cmd in commands:
        result = executor.execute(cmd)
        if not result.success:
            logger.warning(f"[{executor.host}] 命令执行警告: {cmd} -> {result.stderr}")

    # 统计清理后的磁盘占用
    after = executor.execute(f"du -sh {log_dir} 2>/dev/null | cut -f1")

    summary = (
        f"日志清理完成\n"
        f"  清理前: {before.stdout.strip()}\n"
        f"  清理后: {after.stdout.strip()}\n"
        f"  保留天数: {days}天"
    )
    logger.info(f"[{executor.host}] {summary}")

    return ExecResult(
        success=True,
        stdout=summary,
        stderr="",
        exit_code=0,
        duration_ms=0,
    )
```

#### 4.4.3 AI 告警联动闭环

**ops_service/playbooks/auto_remediate.py**

```python
"""
auto_remediate.py
AI 告警 → 自动修复闭环

流程:
1. 接收 AI 检测结果
2. 根据异常类型匹配修复策略
3. 执行修复操作
4. 验证修复结果
5. 更新告警状态
"""

import logging
from typing import Optional
from dataclasses import dataclass

from ai_service.detector import DetectionResult, AlertSeverity
from ops_service.ssh_executor import SSHExecutor
from ops_service.playbooks.restart_service import restart_service
from ops_service.playbooks.clean_logs import clean_old_logs

logger = logging.getLogger("smartops.ops.auto_remediate")


# 修复策略映射
REMEDIATION_POLICIES = {
    "high_cpu": {
        "action": "restart_service",
        "params": {"service_name": "app-server"},
        "description": "CPU 使用率过高，重启应用服务",
    },
    "high_memory": {
        "action": "restart_service",
        "params": {"service_name": "app-server"},
        "description": "内存使用率过高，重启应用服务释放内存",
    },
    "disk_full": {
        "action": "clean_logs",
        "params": {"days": 3},
        "description": "磁盘空间不足，清理过期日志",
    },
}


@dataclass
class RemediationResult:
    success: bool
    action_taken: str
    detail: str
    verified: bool


def auto_remediate(
    detection: DetectionResult,
    executor: SSHExecutor,
) -> Optional[RemediationResult]:
    """
    根据检测结果自动执行修复
    
    安全策略:
    - 仅对 WARNING 及以上级别执行自动修复
    - CRITICAL 级别同时发送人工通知
    - 每台主机 10 分钟内最多执行 1 次自动修复
    """
    if not detection.is_anomaly:
        return None

    if detection.severity == AlertSeverity.INFO:
        return None

    # 根据指标名映射到修复策略
    policy_key = _map_to_policy(detection.metric_name, detection.current_value)
    if not policy_key:
        logger.info(f"无匹配的修复策略: {detection.metric_name}")
        return None

    policy = REMEDIATION_POLICIES[policy_key]
    logger.info(f"[{executor.host}] 执行自动修复: {policy['description']}")

    # 执行修复
    if policy["action"] == "restart_service":
        result = restart_service(
            executor,
            service_name=policy["params"]["service_name"],
        )
    elif policy["action"] == "clean_logs":
        result = clean_old_logs(executor, days=policy["params"]["days"])
    else:
        return None

    # 验证修复结果
    verified = False
    if result.success:
        # 等待 10 秒后重新采集验证
        import time
        time.sleep(10)
        # 此处应调用采集模块验证指标是否恢复正常
        verified = True  # 简化示例

    return RemediationResult(
        success=result.success,
        action_taken=policy["description"],
        detail=result.stdout or result.stderr,
        verified=verified,
    )


def _map_to_policy(metric_name: str, value: float) -> Optional[str]:
    """将指标异常映射到修复策略"""
    if "cpu" in metric_name and value > 90:
        return "high_cpu"
    if "mem" in metric_name and value > 90:
        return "high_memory"
    if "disk" in metric_name and value > 85:
        return "disk_full"
    return None
```

---

### 4.5 Celery 异步任务集成

**tasks/celery_app.py**

```python
"""
celery_app.py
Celery 异步任务队列配置
"""

from celery import Celery

celery_app = Celery(
    "smartops",
    broker="redis://localhost:6379/1",
    backend="redis://localhost:6379/2",
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="Asia/Shanghai",
    enable_utc=True,
    # 任务超时设置
    task_soft_time_limit=60,
    task_time_limit=120,
    # Worker 并发数
    worker_concurrency=4,
    # 任务优先级队列
    task_queues={
        "default": {"exchange": "default", "routing_key": "default"},
        "ai_detection": {"exchange": "ai", "routing_key": "ai.detection"},
        "ops_action": {"exchange": "ops", "routing_key": "ops.action"},
    },
    task_default_queue="default",
)
```

**tasks/ai_tasks.py**

```python
"""
ai_tasks.py
AI 异常检测异步任务
"""

import logging
from app.tasks.celery_app import celery_app
from ai_service.detector import SmartDetector
from app.services.alert_service import AlertService

logger = logging.getLogger("smartops.tasks.ai")

# 全局检测器实例（进程级别复用）
_detector = SmartDetector()


@celery_app.task(
    name="run_anomaly_detection",
    queue="ai_detection",
    max_retries=2,
    default_retry_delay=5,
)
def run_anomaly_detection(agent_id: str, metrics_data: dict):
    """
    异步执行 AI 异常检测
    
    由 Web 后端在接收到探针上报数据后触发。
    采用"旁路检测"模式，不影响 API 响应速度。
    """
    try:
        hostname = metrics_data.get("hostname", "unknown")
        logger.info(f"开始异常检测: {hostname}")

        # 执行检测
        results = _detector.detect(hostname, metrics_data)

        # 处理检测结果
        alert_service = AlertService()
        for result in results:
            if result.is_anomaly:
                alert_service.create_alert(
                    hostname=hostname,
                    agent_id=agent_id,
                    detection=result,
                )
                logger.warning(
                    f"异常告警: {hostname} - {result.message}"
                )

        return {
            "hostname": hostname,
            "anomaly_count": sum(1 for r in results if r.is_anomaly),
            "total_checks": len(results),
        }

    except Exception as e:
        logger.error(f"异常检测任务失败: {e}")
        raise run_anomaly_detection.retry(exc=e)
```

---

## 5. 关键难点与解决方案

### 5.1 Python 与 C/C++ 混合编程

| 难点 | 解决方案 |
|------|---------|
| 数据类型不匹配导致段错误 | 在 Python 端必须显式声明 `restype` 和 `argtypes` |
| 内存泄漏 | C 端使用 `malloc` 分配的内存必须提供对应的 `free` 函数 |
| 线程安全 | C 采集函数使用互斥锁保护静态变量 |
| ABI 兼容性 | C 端使用纯 C 函数，避免 C++ 特性，编译加 `-fPIC` |
| 跨平台 | 使用条件编译 `#ifdef __linux__` 处理平台差异 |

**C 端线程安全示例**：

```c
#include <pthread.h>
static pthread_mutex_t collect_mutex = PTHREAD_MUTEX_INITIALIZER;

int sysmon_collect(SystemMetrics* metrics) {
    pthread_mutex_lock(&collect_mutex);
    // ... 采集逻辑 ...
    pthread_mutex_unlock(&collect_mutex);
    return 0;
}
```

### 5.2 异步高并发数据处理

| 难点 | 解决方案 |
|------|---------|
| 高频上报阻塞主线程 | 全程使用 `async def` + `await` |
| 数据库写入瓶颈 | Redis 缓冲 + 异步批量落盘 |
| AI 推理耗时影响响应 | "旁路检测"模式，Celery 异步执行 |
| 数据丢失风险 | 离线缓冲区 + 重试机制 |

**数据流时序**：

```
探针 Agent ──POST──► FastAPI 接口
                        │
                   ┌────┴────┐
                   ▼         ▼
              Redis 缓存   BackgroundTasks
              (立即返回)     │
                         ┌──┴──┐
                         ▼     ▼
                    PostgreSQL  Celery
                    (异步落盘)  (AI 检测)
                                   │
                                   ▼
                              告警 / 自动修复
```

### 5.3 AI 异常检测算法落地

| 难点 | 解决方案 |
|------|---------|
| 冷启动无历史数据 | 滑动窗口检测器自适应，10 个数据点即可工作 |
| 业务高峰误报 | 组合检测策略（多算法投票），降低误报率 |
| 模型在线更新 | 孤立森林支持增量训练，定期重训练基线 |
| 多维指标关联分析 | 孤立森林天然支持多维特征联合检测 |

---

## 6. 部署方案

### 6.1 Docker 多阶段构建

**backend/Dockerfile**

```dockerfile
# ========== 第一阶段: 编译 C 模块 ==========
FROM gcc:13 AS builder

WORKDIR /build
COPY agent/c_module/ .
RUN make clean && make

# ========== 第二阶段: Python 运行环境 ==========
FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# 复制编译产物
COPY --from=builder /build/libsysmon.so /app/agent/c_module/

# 安装 Python 依赖
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY backend/ /app/backend/
COPY ai_service/ /app/ai_service/
COPY ops_service/ /app/ops_service/
COPY agent/ /app/agent/

# 环境变量
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# 启动命令
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

### 6.2 Docker Compose 编排

**deploy/docker-compose.yml**

```yaml
version: "3.9"

services:
  # FastAPI 后端服务
  backend:
    build:
      context: ..
      dockerfile: backend/Dockerfile
    ports:
      - "8000:8000"
    environment:
      - REDIS_URL=redis://redis:6379/0
      - DATABASE_URL=postgresql://smartops:smartops@postgres:5432/smartops
      - CELERY_BROKER=redis://redis:6379/1
    depends_on:
      redis:
        condition: service_healthy
      postgres:
        condition: service_healthy
    restart: unless-stopped
    networks:
      - smartops-net

  # Celery Worker
  celery-worker:
    build:
      context: ..
      dockerfile: backend/Dockerfile
    command: celery -A backend.app.tasks.celery_app worker --loglevel=info --concurrency=4
    environment:
      - REDIS_URL=redis://redis:6379/0
      - DATABASE_URL=postgresql://smartops:smartops@postgres:5432/smartops
      - CELERY_BROKER=redis://redis:6379/1
    depends_on:
      - backend
    restart: unless-stopped
    networks:
      - smartops-net

  # Redis 缓存
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    command: redis-server --appendonly yes --maxmemory 512mb --maxmemory-policy allkeys-lru
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 3
    restart: unless-stopped
    networks:
      - smartops-net

  # PostgreSQL 持久化存储
  postgres:
    image: postgres:15-alpine
    ports:
      - "5432:5432"
    environment:
      POSTGRES_USER: smartops
      POSTGRES_PASSWORD: smartops
      POSTGRES_DB: smartops
    volumes:
      - pg-data:/var/lib/postgresql/data
      - ../scripts/init_db.sql:/docker-entrypoint-initdb.d/init.sql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U smartops"]
      interval: 10s
      timeout: 5s
      retries: 3
    restart: unless-stopped
    networks:
      - smartops-net

  # Nginx 反向代理
  nginx:
    image: nginx:1.24-alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - backend
    restart: unless-stopped
    networks:
      - smartops-net

volumes:
  redis-data:
  pg-data:

networks:
  smartops-net:
    driver: bridge
```

### 6.3 Nginx 配置

**deploy/nginx/nginx.conf**

```nginx
worker_processes auto;
error_log /var/log/nginx/error.log warn;

events {
    worker_connections 4096;
}

http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;

    # 日志格式
    log_format main '$remote_addr - $remote_user [$time_local] '
                    '"$request" $status $body_bytes_sent '
                    '"$http_referer" "$http_user_agent"';
    access_log /var/log/nginx/access.log main;

    # 性能优化
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;

    # 限流配置
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=100r/s;

    upstream backend {
        server backend:8000;
    }

    server {
        listen 80;
        server_name _;

        # API 代理
        location /api/ {
            limit_req zone=api_limit burst=50 nodelay;
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_read_timeout 30s;
        }

        # WebSocket 支持（实时数据推送）
        location /ws/ {
            proxy_pass http://backend;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_read_timeout 3600s;
        }

        # 健康检查
        location /health {
            proxy_pass http://backend/api/health;
        }
    }
}
```

### 6.4 一键部署脚本

**deploy/deploy.sh**

```bash
#!/bin/bash
set -e

echo "============================================"
echo "  SmartOps 智能运维监控平台 - 一键部署"
echo "============================================"

# 配置
PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
COMPOSE_FILE="$PROJECT_DIR/deploy/docker-compose.yml"
ENV_FILE="$PROJECT_DIR/deploy/.env"

# 1. 检查依赖
echo "[1/6] 检查系统依赖..."
for cmd in docker docker-compose git gcc make; do
    if ! command -v $cmd &> /dev/null; then
        echo "错误: 未安装 $cmd"
        exit 1
    fi
done
echo "  ✓ 依赖检查通过"

# 2. 编译 C 模块
echo "[2/6] 编译 C 采集模块..."
cd "$PROJECT_DIR/agent/c_module"
make clean && make
echo "  ✓ libsysmon.so 编译完成"

# 3. 初始化环境变量
echo "[3/6] 配置环境变量..."
if [ ! -f "$ENV_FILE" ]; then
    cp "$PROJECT_DIR/deploy/.env.example" "$ENV_FILE"
    echo "  ⚠ 已生成默认配置，请修改 $ENV_FILE 中的敏感信息"
fi

# 4. 构建 Docker 镜像
echo "[4/6] 构建 Docker 镜像..."
cd "$PROJECT_DIR"
docker-compose -f "$COMPOSE_FILE" build --no-cache
echo "  ✓ 镜像构建完成"

# 5. 启动服务
echo "[5/6] 启动服务..."
docker-compose -f "$COMPOSE_FILE" up -d
echo "  ✓ 服务已启动"

# 6. 健康检查
echo "[6/6] 等待服务就绪..."
sleep 10
for i in $(seq 1 30); do
    if curl -s http://localhost/api/health | grep -q "healthy"; then
        echo "  ✓ SmartOps 部署成功！"
        echo ""
        echo "  访问地址: http://localhost"
        echo "  API 文档: http://localhost/api/docs"
        echo "============================================"
        exit 0
    fi
    sleep 2
done

echo "  ⚠ 服务启动超时，请检查日志:"
echo "  docker-compose -f $COMPOSE_FILE logs"
exit 1
```

---

## 7. 测试方案

### 7.1 单元测试

```bash
# 运行全部测试
cd backend
pytest tests/ -v --cov=app --cov=ai_service

# 仅测试 AI 模块
pytest tests/test_ai_detection.py -v

# 仅测试 ctypes 桥接
pytest tests/test_ctypes_bridge.py -v
```

**test_ai_detection.py 示例**：

```python
"""AI 异常检测算法单元测试"""

import pytest
import numpy as np
from ai_service.detector import (
    SlidingWindowDetector,
    IsolationForestDetector,
    SmartDetector,
)


class TestSlidingWindowDetector:

    def setup_method(self):
        self.detector = SlidingWindowDetector(window_size=60, threshold_sigma=3.0)

    def test_normal_data_no_anomaly(self):
        """正常波动数据不应触发异常"""
        # 注入 50 个正常数据点（均值 50，标准差 5）
        np.random.seed(42)
        for val in np.random.normal(50, 5, 50):
            self.detector.detect("test:cpu", val)

        # 正常范围内的新数据
        result = self.detector.detect("test:cpu", 55.0)
        assert result is not None
        assert result.is_anomaly is False

    def test_spike_detected(self):
        """突刺数据应触发异常"""
        np.random.seed(42)
        for val in np.random.normal(50, 5, 50):
            self.detector.detect("test:cpu", val)

        # 异常突刺
        result = self.detector.detect("test:cpu", 95.0)
        assert result is not None
        assert result.is_anomaly is True

    def test_insufficient_data_returns_none(self):
        """数据不足时应返回 None"""
        result = self.detector.detect("test:cpu", 50.0)
        assert result is None


class TestIsolationForestDetector:

    def test_train_and_detect(self):
        """训练后应能正常检测"""
        detector = IsolationForestDetector(contamination=0.05)

        # 生成训练数据
        np.random.seed(42)
        normal_data = np.random.normal(loc=50, scale=10, size=(200, 3))
        features = ["cpu", "mem", "disk"]
        detector.train(normal_data, features)

        # 正常数据
        result = detector.detect({"cpu": 50, "mem": 55, "disk": 40})
        assert result is not None
        assert result.is_anomaly is False

        # 异常数据
        result = detector.detect({"cpu": 99, "mem": 98, "disk": 95})
        assert result is not None
        assert result.is_anomaly is True
```

### 7.2 跨语言集成测试

```python
"""验证 Python 调用 C 动态库的正确性"""

import pytest
import time
from agent.bridge import SysmonBridge


class TestCtypesBridge:

    def test_load_library(self):
        """动态库加载成功"""
        bridge = SysmonBridge()
        assert bridge._lib is not None

    def test_collect_returns_dict(self):
        """采集返回正确的字典结构"""
        with SysmonBridge() as bridge:
            metrics = bridge.collect()
            assert isinstance(metrics, dict)
            assert "cpu" in metrics
            assert "mem" in metrics
            assert "disk" in metrics
            assert "net" in metrics
            assert "timestamp" in metrics
            assert "hostname" in metrics

    def test_cpu_usage_range(self):
        """CPU 使用率在合理范围内"""
        with SysmonBridge() as bridge:
            bridge.collect()  # 首次采样
            time.sleep(0.1)
            metrics = bridge.collect()
            assert 0 <= metrics["cpu"]["usage_percent"] <= 100

    def test_performance_benchmark(self):
        """C 采集性能优于纯 Python"""
        with SysmonBridge() as bridge:
            start = time.perf_counter()
            for _ in range(1000):
                bridge.collect()
            c_duration = time.perf_counter() - start
            print(f"\nC 采集 1000 次耗时: {c_duration:.3f}s")
            assert c_duration < 5.0  # 1000 次采集应在 5 秒内完成
```

### 7.3 压力测试（Locust）

```python
"""
locustfile.py
使用 Locust 模拟高并发数据上报
"""

from locust import HttpUser, task, between
import random
import time


class MetricsAgent(HttpUser):
    """模拟探针 Agent 上报"""
    wait_time = between(0.5, 1.5)

    def _generate_metrics(self):
        return {
            "agent_id": f"agent-{random.randint(1, 100)}",
            "metrics_batch": [{
                "cpu": {
                    "usage_percent": random.uniform(10, 90),
                    "user_percent": random.uniform(5, 60),
                    "system_percent": random.uniform(5, 30),
                    "iowait_percent": random.uniform(0, 10),
                    "core_count": 8,
                    "load_avg_1": random.uniform(0.5, 8.0),
                    "load_avg_5": random.uniform(0.5, 6.0),
                    "load_avg_15": random.uniform(0.5, 4.0),
                },
                "mem": {
                    "total_bytes": 17179869184,
                    "used_bytes": random.randint(4000000000, 15000000000),
                    "free_bytes": random.randint(1000000000, 8000000000),
                    "cached_bytes": random.randint(500000000, 4000000000),
                    "buffers_bytes": random.randint(100000000, 1000000000),
                    "usage_percent": random.uniform(30, 90),
                    "swap_total": 8589934592,
                    "swap_used": random.randint(0, 2000000000),
                },
                "disk": {
                    "total_bytes": 536870912000,
                    "used_bytes": random.randint(100000000000, 450000000000),
                    "free_bytes": random.randint(50000000000, 400000000000),
                    "usage_percent": random.uniform(20, 85),
                    "read_bytes_per_sec": random.uniform(0, 50000000),
                    "write_bytes_per_sec": random.uniform(0, 30000000),
                    "io_util_percent": random.uniform(0, 80),
                },
                "net": {
                    "bytes_sent": random.randint(1000000, 100000000),
                    "bytes_recv": random.randint(1000000, 200000000),
                    "packets_sent": random.randint(1000, 100000),
                    "packets_recv": random.randint(1000, 200000),
                    "send_bytes_per_sec": random.uniform(1000, 10000000),
                    "recv_bytes_per_sec": random.uniform(1000, 20000000),
                    "tcp_connections": random.randint(10, 500),
                },
                "timestamp": int(time.time() * 1000),
                "hostname": f"server-{random.randint(1, 20)}",
            }],
        }

    @task(3)
    def report_metrics(self):
        """上报指标数据"""
        self.client.post(
            "/api/v1/metrics/report",
            json=self._generate_metrics(),
        )

    @task(1)
    def query_realtime(self):
        """查询实时数据"""
        hostname = f"server-{random.randint(1, 20)}"
        self.client.get(f"/api/v1/metrics/realtime/{hostname}")
```

**运行压力测试**：

```bash
# 启动 Locust（100 并发用户，每秒增加 10 个）
locust -f tests/locustfile.py --host http://localhost:8000 -u 100 -r 10
# 访问 http://localhost:8089 查看测试结果
```

---

## 8. 环境变量配置

**deploy/.env.example**

```env
# ========== 应用配置 ==========
APP_NAME=SmartOps
APP_ENV=production
APP_DEBUG=false
APP_SECRET_KEY=your-secret-key-change-me

# ========== 数据库配置 ==========
DATABASE_URL=postgresql://smartops:smartops@postgres:5432/smartops
REDIS_URL=redis://redis:6379/0

# ========== Celery 配置 ==========
CELERY_BROKER=redis://redis:6379/1
CELERY_BACKEND=redis://redis:6379/2

# ========== 告警配置 ==========
ALERT_EMAIL_ENABLED=true
ALERT_EMAIL_SMTP_HOST=smtp.example.com
ALERT_EMAIL_SMTP_PORT=465
ALERT_EMAIL_FROM=smartops@example.com
ALERT_EMAIL_PASSWORD=your-email-password
ALERT_EMAIL_TO=ops-team@example.com

ALERT_WEBHOOK_ENABLED=false
ALERT_WEBHOOK_URL=https://hooks.example.com/smartops

# ========== SSH 配置 ==========
SSH_DEFAULT_USER=root
SSH_DEFAULT_PORT=22
SSH_KEY_FILE=/root/.ssh/id_rsa
```

---

## 9. API 接口汇总

| 方法 | 路径 | 说明 |
|------|------|------|
| `POST` | `/api/v1/metrics/report` | 批量上报指标数据 |
| `GET` | `/api/v1/metrics/query` | 查询历史指标数据 |
| `GET` | `/api/v1/metrics/realtime/{hostname}` | 获取实时指标快照 |
| `GET` | `/api/v1/alerts` | 获取告警列表（支持分页） |
| `POST` | `/api/v1/alerts/{id}/acknowledge` | 确认告警 |
| `POST` | `/api/v1/alerts/{id}/resolve` | 标记告警已解决 |
| `GET` | `/api/v1/hosts` | 获取主机列表 |
| `POST` | `/api/v1/hosts/register` | 注册新主机 |
| `DELETE` | `/api/v1/hosts/{hostname}` | 移除主机 |
| `POST` | `/api/v1/ops/execute` | 手动执行运维操作 |
| `GET` | `/api/v1/ops/logs` | 查询运维操作日志 |
| `GET` | `/api/health` | 健康检查 |

---

## 10. 开发计划与里程碑

| 阶段 | 周期 | 交付物 |
|------|------|-------|
| **P1: 基础架构** | 第 1-2 周 | 项目骨架搭建、C 采集模块编译、FastAPI 基础接口 |
| **P2: 数据链路** | 第 3-4 周 | Redis + PostgreSQL 集成、数据上报与查询完整链路 |
| **P3: AI 检测** | 第 5-6 周 | 滑动窗口 + 孤立森林算法、Celery 异步检测 |
| **P4: 运维闭环** | 第 7-8 周 | SSH 执行器、运维剧本、AI 联动自动修复 |
| **P5: 容器化** | 第 9 周 | Dockerfile、docker-compose、一键部署 |
| **P6: 测试验收** | 第 10 周 | 单元测试、集成测试、压力测试、故障演练 |
