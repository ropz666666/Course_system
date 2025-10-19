import {Checkbox, Card, Button, Divider, Space, Typography, message, Alert, Modal, Descriptions, Input} from 'antd';
import { LeftOutlined } from "@ant-design/icons";
import { useNavigate } from "react-router-dom";
import {useEffect, useState} from "react";
import { useAgentSelector, useDispatchAgent } from "../../hooks/agent.ts";
import { useDispatchAgentPublishment } from "../../hooks/publish.ts";
const { Title, Text } = Typography;

interface Publishment {
    uuid: string;
    channel_uuid: string;
    publish_config?: Record<string, unknown>;
}
type PlatformOption = {
    uuid: string;
    key: string;
    title: string;
    description: string;
    disabled: boolean;
    disabledReason?: string;
    publish_config?: Record<string, unknown>;
}

// 发布平台选项数据
const platformOptions: PlatformOption[]= [
    {
        uuid: 'a0c43b23-2201-11f0-a583-0250f2000002',
        key: 'api',
        title: 'API',
        description: '在发布前请先创建个人令牌。',
        disabled: false,
        publish_config: {
            plugin_uuid: ''
        }
    },
    {
        uuid: 'a0c4a0e6-2201-11f0-a583-0250f2000002',
        key: 'chatSdk',
        title: 'Chat SDK',
        description: '将项目部署到SDK，支持多种客户端接入',
        disabled: true,
        disabledReason: '即将推出'
    },
    {
        uuid: 'a0c4bda1-2201-11f0-a583-0250f2000002',
        key: 'douyin',
        title: '抖音小程序',
        description: '发布到抖音小程序平台',
        disabled: true,
        disabledReason: '即将推出'
    },
    {
        uuid: 'a0c4bee4-2201-11f0-a583-0250f2000002',
        key: 'wechatMini',
        title: '微信小程序',
        description: '发布到微信小程序平台',
        disabled: true,
        disabledReason: '即将推出'
    },
    {
        uuid: 'a0c4bfaf-2201-11f0-a583-0250f2000002',
        key: 'wechatSubscribe',
        title: '微信订阅号',
        description: '发布到微信订阅号平台',
        disabled: false,
        publish_config: {
            "URL": '',
            "Token": '',
            'EncodingAESKey': ''
        }
    },
    {
        uuid: 'a0c4bf49-2201-11f0-a583-0250f2000002',
        key: 'wechatOfficial',
        title: '微信公众号',
        description: '发布到微信服务号平台',
        disabled: true,
        disabledReason: '即将推出'
    },
    {
        uuid: 'a0c4c008-2201-11f0-a583-0250f2000002',
        key: 'portalProduct',
        title: 'Sapper商店',
        description: '应用会出现在项目商店中，为你的应用获取更多的曝光和流量',
        disabled: false,
        publish_config: {}
    },
    {
        uuid: 'a0c4c102-2201-11f0-a583-0250f2000002',
        key: 'template',
        title: '模板',
        description: '将应用发布为模板，支持直接购买或复制体验。',
        disabled: true,
        disabledReason: '即将推出'
    },
    {
        uuid: 'a0c4c170-2201-11f0-a583-0250f2000002',
        key: 'mcp',
        title: '门户空间扩展',
        description: '扩展门户空间功能',
        disabled: true,
        disabledReason: '即将推出'
    }
];


const AgentPublishPage = () => {
    const navigate = useNavigate();
    const agentDispatch = useDispatchAgent();
    const agentPublishmentDispatch = useDispatchAgentPublishment();
    const agentDetail = useAgentSelector(state => state.agent.agentDetail);

    // 状态管理
    const [publishedChannels, setPublishedChannels] = useState<Set<string>>(new Set());
    const [selectedChannels, setSelectedChannels] = useState<Set<string>>(new Set());
    const [configVisible, setConfigVisible] = useState(false);
    const [selectedConfig, setSelectedConfig] = useState<Record<string, unknown> | null>(null);
    const [channelPublishmentMap, setChannelPublishmentMap] = useState<Map<string, Publishment>>(new Map());
    const [cancelLoadingId, setCancelLoadingId] = useState<string | null>(null);

    useEffect(() => {
        const pathSegments = location.pathname.split("/");
        const agentId = pathSegments[pathSegments.length - 2];
        // eslint-disable-next-line @typescript-eslint/no-unused-expressions
        agentId && agentDispatch.getAgentDetail(agentId);
    }, [location.pathname]);

    // 初始化发布状态
    useEffect(() => {
        if (agentDetail?.publishments) {
            const map = new Map(
                agentDetail.publishments.map(p => [p.channel_uuid, p])
            );
            setChannelPublishmentMap(map);

            const published = new Set(
                agentDetail.publishments.map(p => p.channel_uuid)
            );
            setPublishedChannels(published);
        }
    }, [agentDetail]);

    // 处理平台选择
    const handleSelect = (option: PlatformOption) => {
        if (option.disabled || publishedChannels.has(option.uuid)) return;

        setSelectedChannels(prev => {
            const newSet = new Set(prev);
            // eslint-disable-next-line @typescript-eslint/no-unused-expressions
            newSet.has(option.key) ? newSet.delete(option.key) : newSet.add(option.key);
            return newSet;
        });
    };

    // 处理发布操作
    const handlePublish = async () => {
        if (!agentDetail || selectedChannels.size === 0) {
            message.error('请至少选择一个发布平台');
            return;
        }


        try {
            const channels = Array.from(selectedChannels)
                .map(key => platformOptions.find(opt => opt.key === key))
                .filter(opt => opt && !publishedChannels.has(opt.uuid))
                .map(opt => ({ channel_uuid: opt!.uuid }));

            if (channels.length === 0) {
                message.error('没有新的发布渠道可选');
                return;
            }

            await agentPublishmentDispatch.addAgentPublishment({
                agent_uuid: agentDetail.uuid,
                channels
            });

            // 刷新数据
            await agentDispatch.getAgentDetail(agentDetail.uuid);
            message.success('发布成功');
        } catch {
            message.error('发布失败');
        }
    };

    // 取消发布
    const handleCancelPublish = async (publishment: Publishment) => {
        Modal.confirm({
            title: '确认取消发布？',
            content: '取消后该平台将不再展示你的智能体',
            okText: '确认',
            cancelText: '取消',
            onOk: async () => {
                try {
                    setCancelLoadingId(publishment.uuid);
                    await agentPublishmentDispatch.removeAgentPublishment(publishment.uuid);

                    // 更新本地状态
                    setPublishedChannels(prev => {
                        const newSet = new Set(prev);
                        newSet.delete(publishment.channel_uuid);
                        return newSet;
                    });

                    setChannelPublishmentMap(prev => {
                        const newMap = new Map(prev);
                        newMap.delete(publishment.channel_uuid);
                        return newMap;
                    });

                    message.success('已取消发布');
                } catch{
                    message.error('取消发布失败');
                } finally {
                    setCancelLoadingId(null);
                }
            }
        });
    };

    // 渲染平台卡片
    const renderPlatformCard = (option: PlatformOption, interactive = true) => {
        const isPublished = publishedChannels.has(option.uuid);
        const publishment = channelPublishmentMap.get(option.uuid);
        const hasConfig = isPublished && publishment?.publish_config && Object.keys(publishment.publish_config).length > 0;
        const isSelected = selectedChannels.has(option.key);
        const isDisabled = option.disabled || isPublished;

        return (
            <Card
                key={option.key}
                hoverable={!isDisabled}
                onClick={() => interactive && handleSelect(option)}
                style={{
                  width: '100%',
                  border: `1px solid ${isDisabled ? '#f0f0f0' : '#d9d9d9'}`,
                  backgroundColor: isPublished ? '#f6ffed' : isSelected ? '#e6f7ff' : 'white',
                  opacity: isDisabled ? 0.6 : 1,
                  cursor: isDisabled ? 'not-allowed' : 'pointer',
                  transition: 'all 0.2s'
                }}
            >
                <div style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'flex-start'
                }}>
                  <div style={{ flex: 1 }}>
                    <Text strong>
                      {option.title}
                      {isPublished && (
                        <span style={{
                          color: '#52c41a',
                          marginLeft: 8,
                          fontSize: 12
                        }}>(已发布)</span>
                      )}
                    </Text>
                    <div style={{ marginTop: 8, color: '#666' }}>
                      {option.description}
                    </div>

                    {/* 操作按钮区域 */}
                    <div style={{ marginTop: 8, display: 'flex', gap: 8 }}>
                      {hasConfig && (
                        <Button
                          type="link"
                          size="small"
                          style={{ paddingLeft: 0 }}
                          onClick={(e) => {
                            e.stopPropagation();
                            setSelectedConfig(publishment.publish_config!);
                            setConfigVisible(true);
                          }}
                        >
                          查看配置
                        </Button>
                      )}

                      {isPublished && (
                        <Button
                          type="link"
                          size="small"
                          danger
                          loading={cancelLoadingId === publishment?.uuid}
                          onClick={(e) => {
                            e.stopPropagation();
                            if(publishment)
                                handleCancelPublish(publishment);
                          }}
                        >
                          取消发布
                        </Button>
                      )}
                    </div>

                    {option.disabled && (
                      <div style={{ color: '#ff4d4f', marginTop: 8 }}>
                        {option.disabledReason || '暂不可用'}
                      </div>
                    )}
                  </div>
                  <Checkbox
                    checked={isSelected || isPublished}
                    disabled={isDisabled}
                    style={{ marginLeft: 8 }}
                  />
                </div>
            </Card>
        );
    };

  // 渲染平台分组
  const renderSection = (title: string, options: PlatformOption[], interactive = true) => (
    <div style={{ marginBottom: 24 }}>
      <Text strong style={{ display: 'block', marginBottom: 16, fontSize: 16 }}>
        {title}
      </Text>
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
        gap: 16
      }}>
        {options.map(opt => renderPlatformCard(opt, interactive))}
      </div>
    </div>
  );

  // 分组配置
  const apiGroup = platformOptions.filter(opt => ['api', 'chatSdk'].includes(opt.key));
  const miniProgramGroup = platformOptions.filter(opt => ['douyin', 'wechatMini'].includes(opt.key));
  const socialGroup = platformOptions.filter(opt => ['wechatOfficial', 'wechatSubscribe'].includes(opt.key));
  const portalGroup = platformOptions.filter(opt => ['portalProduct', 'template'].includes(opt.key));
  const mcpGroup = platformOptions.filter(opt => ['mcp'].includes(opt.key));

  return (
    <div style={{
      minHeight: '100vh',
      backgroundColor: '#f7f7fc',
      paddingTop: 60
    }}>
      {/* 头部导航 */}
      <div style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        zIndex: 100,
        height: 60,
        padding: '0 24px',
        backgroundColor: 'white',
        borderBottom: '1px solid #f0f0f0',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)'
      }}>
        <Space>
          <Button
            icon={<LeftOutlined />}
            onClick={() => navigate(`/workspace/agent/${agentDetail?.uuid}`)}
            type="text"
            style={{ fontSize: 16 }}
          />
          <Text strong style={{ fontSize: 16 }}>发布智能体</Text>
        </Space>
        <Button
          type="primary"
          style={{
            background: 'linear-gradient(135deg, #6a11cb, #2575fc)',
            fontWeight: 'bold'
          }}
          onClick={handlePublish}
        >
          发布
        </Button>
      </div>

      <Alert
        message="建议完成试运行后再发布"
        type="warning"
        showIcon
        closable
        style={{ margin: 16 }}
      />

      {/* 主要内容区域 */}
      <div style={{
        maxWidth: 800,
        margin: '0 auto',
        padding: 24
      }}>
        <Card variant={"borderless"} style={{ borderRadius: 8 }}>
          <Title level={4} style={{ marginBottom: 16 }}>选择发布平台</Title>
          <Text type="secondary" style={{ display: 'block', marginBottom: 24 }}>
            发布即表示同意各平台服务条款
          </Text>

          {renderSection('Sapper', portalGroup)}
          <Divider style={{ margin: '24px 0' }} />

          {renderSection('API 或 SDK', apiGroup)}
          <Divider style={{ margin: '24px 0' }} />

          {renderSection('社交平台', socialGroup)}
          <Divider style={{ margin: '24px 0' }} />

          {renderSection('小程序', miniProgramGroup, false)}
          <Divider style={{ margin: '24px 0' }} />

          {renderSection('MCP服务', mcpGroup, false)}
        </Card>
      </div>

      {/* 配置信息弹窗 */}
        <Modal
            title="发布配置信息"
            width={'60%'}
            open={configVisible}
            onCancel={() => setConfigVisible(false)}
            footer={[
                <Button key="close" onClick={() => setConfigVisible(false)}>
                    关闭
                </Button>
            ]}
        >
            {selectedConfig ? (
                <div style={{ maxHeight: '60vh', overflow: 'auto', width: '100%'}}>
                    <Descriptions bordered column={1} size="small">
                        {Object.entries(selectedConfig).map(([key, value]) => (
                            <Descriptions.Item key={key} label={key}>
                                {value ? <Input.TextArea variant={"borderless"} value={value.toString()} autoSize /> : <span style={{ color: '#999' }}>空值</span>}
                            </Descriptions.Item>
                        ))}
                    </Descriptions>
                </div>
            ) : (
                <Text type="secondary">暂无配置信息</Text>
            )}
        </Modal>
    </div>
  );
};

export default AgentPublishPage;