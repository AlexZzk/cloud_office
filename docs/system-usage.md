# Cloud Office 系统使用文档（Office Module）

> 本文档面向当前仓库中的基础办公室模块，后续随着能力迭代持续更新。

## 1. 如何启动

当前仓库提供两种启动方式：

1. **模块验证模式**：通过单元测试验证办公室能力；
2. **Demo 服务模式**：启动一个可直接访问的前后端示例服务，页面可看到 2D 场景聚合结果。

### 1.1 环境要求

- Python 3.10+
- 无需外部数据库（当前默认 InMemory）

### 1.2 安装与准备

```bash
git clone <your-repo-url>
cd cloud_office
```

> 注意：当前示例不依赖额外三方包，使用标准库 `unittest` 即可运行。

### 1.3 启动方式 A：模块验证（开发测试）

执行完整测试即视为完成一次模块能力验证：

```bash
python -m unittest discover -s tests -v
```

覆盖流程包含：
- 模板创建、办公室创建
- 办公室激活/停用
- Presence 进入/移动/离开
- 场景绑定切换
- 2D 场景 gather 聚合

### 1.4 启动方式 B：Demo 服务（可直接访问）

```bash
python -m office_module.server --host 127.0.0.1 --port 8080
```

启动后可访问：

- 页面：`http://127.0.0.1:8080/`
- 场景聚合接口：`http://127.0.0.1:8080/api/scene/gathered`
- 健康检查：`http://127.0.0.1:8080/health`

> 注意：当前 Demo 使用内存数据，重启服务后会重置为默认示例办公室与场景。

---

## 2. 使用注意事项

### 2.1 当前运行形态

- 当前为**模块级实现**，不是完整 HTTP 服务进程。
- 入口为 Python 类 `office_module.OfficeModule`，适合在上层 API/BFF 中集成。

### 2.2 数据持久化

- 默认使用 InMemory 仓储：进程结束后数据会丢失。
- 生产化需要实现并注入 PostgreSQL/Redis 等持久化适配器。

### 2.3 场景与办公室解耦

- 办公室域对象使用业务语义（zone/seat/position_token），不使用像素坐标。
- 渲染坐标映射由场景绑定与 gather 逻辑负责，切换场景不会改动办公室核心数据。

### 2.4 错误与约束

- 办公室未激活时不可 `enter_office`。
- 场景绑定要求映射完整（模板中的 zone/seat 必须被映射）。
- 容量超限时新参与者进入会失败。

---

## 3. 扩展设计说明（持续迭代）

本节用于指导后续开发中的扩展方式。原则：**最小颗粒度 + 扩展优先 + 不破坏已有能力**。

### 3.1 核心扩展点总览

1. **应用服务扩展**（`office_module/application/service.py`）
   - 新增命令能力时优先增加独立方法（如 `deactivate_office`），避免改写既有行为。
2. **Port 扩展**（`office_module/ports.py` + `office_module/scene/ports.py`）
   - 先定义接口，再新增适配器，确保领域层不依赖基础设施细节。
3. **适配器扩展**（`office_module/infrastructure/`、`office_module/scene/in_memory.py`）
   - 以新增实现类方式扩展（如 `PostgresOfficeRepo`、`RedisPresenceRepo`）。
4. **场景扩展**（`office_module/scene/`）
   - 已支持 2D/3D 维度声明（`SceneDimension`）。
   - 后续可新增 `Office3DSceneGatherService`，不影响 2D gather。

### 3.2 推荐扩展流程

1. 在 `docs/requirements/` 明确新增能力边界与验收标准。
2. 增加/调整 Domain Model（必要时）。
3. 在 Port 层增加最小接口。
4. 在应用服务层实现命令或查询能力。
5. 在基础设施层补齐适配器实现。
6. 在 `tests/` 先补测试，再实现代码（TDD 优先）。
7. 更新本文档“扩展设计说明”与“已支持能力清单”。

### 3.3 场景模块扩展示例

- 新增 3D gather：
  - 新建 `office_module/scene/service_3d.py`
  - 定义 `Office3DSceneGatherService.gather(...)`
  - 输入继续使用业务布局 + mapping + presence
  - 输出改为 3D 场景节点（mesh/anchor 等）

### 3.4 文档迭代约定

每次新增能力后，请至少更新：

- 本文档：
  - 启动或使用方式是否变化
  - 增加了哪些可扩展点
- `tests/test_office_module.py`：
  - 对应新增能力的回归测试

---

## 4. 当前能力清单（截至本版本）

- 办公室模板创建
- 办公室实例创建
- 办公室激活 / 停用 / 归档
- Presence：进入 / 移动 / 离开 / 查询
- 场景绑定与映射完整性校验
- 场景接口层（2D/3D 定义）
- 首个办公室 2D gather 场景聚合
