# 办公室模块核心能力架构设计（v0.1）

## 1. 目标与约束

本设计只聚焦 **Office 模块**，目标是在没有 Employee / Asset / Web3 等其它模块时，仍可独立运行并对外提供稳定能力。

### 1.1 核心目标

1. Office 模块可单独部署、单独运行。
2. 2D 场景只是展示层，可随时替换，不影响办公室业务能力。
3. 场景切换、皮肤更换、地图变更，不影响办公室实例、座位、规则等核心数据。
4. 后续可通过接口接入员工模块、资产模块，而不反向耦合。

### 1.2 设计约束

- UI 引擎可替换（Canvas/Pixi/Phaser/Unity WebGL 都可），业务域不可绑定某一渲染框架。
- 办公室领域对象必须脱离“像素坐标”语义，使用通用空间语义。
- 事件与命令分离，保障可审计和可回放。

---

## 2. 总体架构（分层）

采用「六边形架构 + 可替换渲染适配器」：

```text
┌─────────────────────────────────────────┐
│            Office Application           │
├─────────────────────────────────────────┤
│ API Layer (REST/WebSocket)             │
│ - OfficeController                      │
│ - PresenceGateway                       │
├─────────────────────────────────────────┤
│ Application Layer                       │
│ - OfficeCommandService                  │
│ - OfficeQueryService                    │
│ - SceneBindingService                   │
├─────────────────────────────────────────┤
│ Domain Layer                            │
│ - Entities: OfficeTemplate/Instance     │
│ - VO: Seat/Zone/Capacity/Policy         │
│ - Domain Events                         │
├─────────────────────────────────────────┤
│ Ports                                   │
│ - OfficeRepoPort                        │
│ - SceneRepoPort                         │
│ - EventBusPort                          │
│ - PresencePort                          │
├─────────────────────────────────────────┤
│ Adapters                                │
│ - PostgreSQL/Redis                      │
│ - InMemory（单机开发）                   │
│ - 2D Renderer Adapter                   │
└─────────────────────────────────────────┘
```

关键点：

- **Domain 不感知 2D**：域层只知道空间节点、工位、区域、容量、规则。
- **2D Renderer Adapter**：把域对象映射到具体场景节点和贴图。
- **SceneBindingService**：单独维护“业务对象 <-> 场景资源”绑定关系。

---

## 3. Office 模块能力边界

## 3.1 Office 模块内聚能力（本模块负责）

- 办公室模板管理（模板创建、版本化）。
- 办公室实例生命周期（创建、启用、停用、归档）。
- 空间结构管理（区域、座位、容量、规则）。
- 在线房间运行时（进入、离开、位置广播、状态同步）。
- 场景绑定与切换（不改业务数据，仅切换展示资源）。

## 3.2 Office 模块不负责（外部模块负责）

- 员工主体创建、员工人事状态。
- 资产铸造、交易、钱包签名。
- 组织架构审批流（可通过外部回调联动）。

---

## 4. 核心领域模型

## 4.1 实体

### OfficeTemplate
- `templateId`
- `name`
- `spaceSchema`（区域/座位/规则的业务定义）
- `defaultSceneBindingId`
- `version`

### OfficeInstance
- `officeId`
- `templateId`
- `ownerOrgId`
- `status`（ACTIVE/INACTIVE/ARCHIVED）
- `runtimePolicy`（容量、访客策略、开放时段）

### SceneBinding
- `sceneBindingId`
- `officeId` 或 `templateId`
- `rendererType`（pixi/phaser/unity-webgl/...）
- `sceneAssetRef`（资源地址/版本）
- `mappingRules`（业务坐标到场景节点映射）

### PresenceSession
- `sessionId`
- `officeId`
- `subjectId`（可先使用 userId 占位，后续可接 employeeId）
- `positionToken`（抽象位置，不直接使用像素）
- `status`（ONLINE/AWAY/BUSY）

## 4.2 值对象

- `Zone`：区域（工位区/会议区/休息区）
- `Seat`：座位（可占用、可预约、可共享）
- `CapacityRule`：容量规则（峰值人数、区域上限）
- `AccessPolicy`：访问策略（私有/组织内/公开）

## 4.3 领域事件

- `OfficeCreated`
- `OfficeActivated`
- `SceneBindingChanged`
- `ParticipantEnteredOffice`
- `ParticipantMoved`
- `ParticipantLeftOffice`
- `OfficeArchived`

---

## 5. “2D 只是展示层”的落地策略

## 5.1 双坐标系统

- **Business Coordinate（业务坐标）**：例如 `ZONE_A.SEAT_12` 或 `NODE_MEETING_3`。
- **Render Coordinate（渲染坐标）**：像素点 `(x, y, layer)`。

只在渲染适配层做转换：

`Business Coordinate -> Mapping Rules -> Render Coordinate`

这保证了：

- 业务逻辑不依赖某个地图文件。
- 更换地图只要更新 `SceneBinding + MappingRules`。

## 5.2 场景切换机制

场景切换不改 Office 业务实体，只改绑定：

1. 新建或选择 `SceneBinding`。
2. 校验映射完整性（所有必须业务节点可映射）。
3. 发布 `SceneBindingChanged` 事件。
4. 前端拉取新场景资源并热更新。

## 5.3 无场景降级运行

即使没有任何 2D 场景资源，Office 模块仍可运行：

- API 正常响应（模板、实例、座位、入场、离场）。
- Presence 可通过文本列表展示。
- 事件照常输出，便于调试和自动化测试。

---

## 6. 对外接口设计（先独立可跑）

## 6.1 REST API（核心）

- `POST /offices/templates`：创建模板
- `POST /offices`：创建办公室实例
- `POST /offices/{officeId}/activate`：启用
- `POST /offices/{officeId}/archive`：归档
- `PUT /offices/{officeId}/scene-binding`：切换场景绑定
- `GET /offices/{officeId}`：查询办公室详情
- `GET /offices/{officeId}/layout`：查询业务布局

## 6.2 Presence API

- `POST /offices/{officeId}/enter`：进入办公室
- `POST /offices/{officeId}/move`：更新位置（业务坐标）
- `POST /offices/{officeId}/leave`：离开办公室
- `GET /offices/{officeId}/presence`：在线列表

## 6.3 WebSocket（可选）

- Topic: `office.{officeId}.presence`
- 广播：进入/移动/离开/状态变化

---

## 7. 存储与运行时建议

## 7.1 存储

- PostgreSQL：模板、实例、策略、场景绑定。
- Redis：在线状态、短期位置、房间广播索引。
- 事件日志表（或 Kafka）：事件追溯。

## 7.2 独立部署模式

- `office-api`：HTTP + WS 服务。
- `office-worker`：异步事件处理（可选）。
- `office-renderer-adapter`：前端 SDK / BFF 适配层（可独立版本）。

---

## 8. 与外部模块集成策略（未来）

为保证低耦合，先定义扩展端口：

- `ParticipantDirectoryPort`：查询参与者元信息（昵称、头像）。
- `OwnershipPort`：查询办公室持有关系（后续接 Web3/资产模块）。
- `AssignmentPort`：查询“谁可被引入”（后续接员工模块）。

Office 内部只依赖这些 Port，不依赖具体模块实现。

---

## 9. MVP 实施顺序（办公室优先）

### 阶段 A：纯后端独立可用

1. 完成模板/实例/布局/场景绑定 API。
2. 完成 Presence enter/move/leave + 在线查询。
3. 完成 InMemory + PostgreSQL 双存储实现。
4. 提供最小 CLI 或 Swagger 演示流程。

### 阶段 B：接 2D 展示层

1. 实现一个默认渲染适配器（建议 Pixi 或 Phaser）。
2. 通过 SceneBinding 拉取资源并渲染。
3. 支持场景热切换，不中断业务会话。

### 阶段 C：稳定性与观测

1. 增加事件审计与回放。
2. 增加容量压测与限流。
3. 增加异常降级（无场景/场景加载失败）。

---

## 10. 验收标准（办公室模块）

1. 在未接员工模块、未接资产模块时，Office API 能完整跑通创建-启用-入场-移动-离场流程。
2. 同一办公室可切换至少两套 2D 场景资源，且业务数据（容量、座位、在线会话）不丢失。
3. 场景文件不可用时，系统可降级为“无场景模式”继续运行。
4. 领域事件可追溯，至少覆盖创建、激活、场景切换、进入/离开。

---

## 11. 下一步输出建议

下一步建议直接产出三份技术文档并行推进开发：

1. 《Office API OpenAPI 草案》
2. 《SceneBinding 映射规则规范》
3. 《Presence 一致性与广播协议》

