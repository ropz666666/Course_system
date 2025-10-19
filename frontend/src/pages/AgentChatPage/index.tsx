import { useEffect, useState } from 'react';
import { useConversationSelector, useDispatchConversation } from "../../hooks/conversation.ts";
import {
    Button,
    Layout,
    Menu,
    Modal,
    Image,
    Dropdown,
    message, List, Avatar,
} from "antd";
import Sider from "antd/es/layout/Sider";
import { Content } from "antd/es/layout/layout";
import EmulatorComponent from "../../components/EmulatorComponent";
import { useLocation, useNavigate } from "react-router-dom";
import {
    MenuFoldOutlined,
    MessageOutlined,
    MenuUnfoldOutlined,
    MoreOutlined,
    EditOutlined,
    DeleteOutlined, UserOutlined, SettingOutlined, MailOutlined, LogoutOutlined, EyeOutlined
} from "@ant-design/icons";
import webIcon from "../../assets/images/icon.png";
import {useAgentSelector, useDispatchAgent} from "../../hooks/agent.ts";
import {AgentRes} from "../../types/agentType.ts";

const AgentChatPage = () => {
    const conversationDispatch = useDispatchConversation();
    const conversations = useConversationSelector((state) => state.conversation.conversations);
    const [conversationUuid, setConversationUuid] = useState<string | null>(null);
    const agentDispatch = useDispatchAgent();
    const agents = useAgentSelector((state) => state.agent.agents);
    const [hoveredConversationUuid, setHoveredConversationUuid] = useState<string | null>(null);
    const [renameModalVisible, setRenameModalVisible] = useState(false);
    const [newConversationModalVisible, setNewConversationModalVisible] = useState(false);
    const [renamingConversationUuid, setRenamingConversationUuid] = useState<string | null>(null);
    const [newName, setNewName] = useState('');
    const location = useLocation();
    const navigate = useNavigate();
    const [loading, setLoading] = useState(false);
    const [pagination, setPagination] = useState({
        current: 1,
        pageSize: 20,
    });
    
    useEffect(() => {
        const lastPartOfPath = location.pathname.split("/").pop() as string;
        if (lastPartOfPath)
            setConversationUuid(lastPartOfPath);
    }, [location.pathname]);

    useEffect(() => {
        loadConversations();
        agentDispatch.getAgentList({size: 40});
    }, [pagination]);

    const loadConversations = async () => {
        setLoading(true);
        try {
            await conversationDispatch.getConversationList({
                page: pagination.current,
                size: pagination.pageSize
            });
        } finally {
            setLoading(false);
        }
    };

    const handleConversationSelect = (uuid: string) => {
        navigate(`/conversation/${uuid}`);
    };

    const handleNewConversation = async (agent: AgentRes) => {
        try {
            const newName = `新会话 @${agent.name}`;
            const res =  await conversationDispatch.addConversation({
                agent_uuid: agent.uuid,
                name: newName
            }).unwrap();
            navigate(`/conversation/${res.uuid}`);
            message.success('会话创建成功');
        } catch (error) {
            console.log(error)
            message.error('创建会话失败');
        }
        setNewConversationModalVisible(false)
    };

    const handleViewConversationAgent = (agent_uuid: string) => {
        try {
            window.location.href = `/agent/display/${agent_uuid}`;
        } catch (error) {
            console.log(error)
            message.error('查看失败');
        }
    };

    const items = conversations?.items.map((item) => ({
        key: item.uuid,
        label: (
            <div
                onClick={() => handleConversationSelect(item.uuid)}
                onMouseEnter={() => setHoveredConversationUuid(item.uuid)}
                onMouseLeave={() => setHoveredConversationUuid(null)}
                style={{
                    color: 'black',
                    display: "flex",
                    justifyContent: "space-between",
                    width: "100%",
                    alignItems: "center",
                    padding: '8px 8px',
                    borderRadius: '4px',
                    transition: 'background-color 0.3s',
                }}
                key={item.uuid}
            >
                <span style={{maxWidth: '120px', overflow: 'hidden'}}>
                    {item.name}
                </span>
                {(item.uuid === conversationUuid || hoveredConversationUuid === item.uuid) && (
                    <Dropdown
                        arrow
                        overlay={(
                            <Menu>
                                <Menu.Item
                                    key="view"
                                    onClick={() => {
                                        handleViewConversationAgent(item.agent_uuid)
                                    }}
                                >
                                    <EyeOutlined style={{ marginRight: '5px' }} /> 查看会话智能体
                                </Menu.Item>
                                <Menu.Item
                                    key="edit"
                                    onClick={() => {
                                        setRenamingConversationUuid(item.uuid);
                                        setNewName(item.name);
                                        setRenameModalVisible(true);
                                    }}
                                >
                                    <EditOutlined style={{ marginRight: '5px' }} /> 重命名
                                </Menu.Item>
                                <Menu.Item
                                    key="delete"
                                    style={{ color: 'red' }}
                                    onClick={() => {
                                        Modal.confirm({
                                            title: "永久删除对话",
                                            content: "删除后，该对话将不可恢复，包括在该对话上传的文档，确认删除吗？",
                                            onOk: async () => {
                                                try {
                                                    // 如果当前选中的会话是要删除的会话，则清空选中状态
                                                    if (item.uuid === conversationUuid) {
                                                        handleConversationSelect('');
                                                    }

                                                    // 删除会话
                                                    await conversationDispatch.removeConversation(item.uuid);

                                                    // 获取剩余的会话列表
                                                    const remainingConversations = conversations.items.filter(conv => conv.uuid !== item.uuid);

                                                    // 如果还有剩余会话，导航到第一个会话
                                                    if (remainingConversations.length > 0) {
                                                        navigate(`/conversation/${remainingConversations[0].uuid}`);
                                                    } else {
                                                        // 如果没有剩余会话，导航到默认页面
                                                        navigate('/conversation');
                                                    }
                                                } catch (error) {
                                                    console.error('删除会话失败:', error);
                                                }
                                            },
                                        });
                                    }}
                                >
                                    <DeleteOutlined style={{ marginRight: '5px' }} /> 删除
                                </Menu.Item>
                            </Menu>
                        )}
                    >
                        <Button icon={<MoreOutlined />} type="text" />
                    </Dropdown>
                )}
            </div>
        ),
    }));

    const [collapsed, setCollapsed] = useState(false);

    return (
        <Layout style={{ minHeight: '100vh' }}>
            <Sider
                width={210}
                theme="light"
                collapsed={collapsed}
                collapsible
                trigger={null}
                style={{
                    position: "relative",
                    backgroundColor: '#f9fbff',
                }}
            >
                {/* 侧边栏顶部 Logo 和标题 */}
                <div style={{
                    padding: '16px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: collapsed ? 'center' : 'space-between',
                    backgroundColor: '#f9fbff',
                    borderBottom: '1px solid #e8e8e8',
                }}>
                    <div style={{display: 'flex', alignItems: 'center'}}>
                        {collapsed && <Image src={webIcon} width={40} height={40} preview={false}/>}
                        {!collapsed && (
                            <span style={{marginLeft: '10px', fontSize: '18px', fontWeight: 'bold'}} onClick={() => navigate(`/workspace/agent`)}>
                                智能体创建平台
                            </span>
                        )}
                    </div>
                    {!collapsed && (
                        <MenuFoldOutlined
                            style={{fontSize: '18px', cursor: 'pointer'}}
                            onClick={() => setCollapsed(true)}
                        />
                    )}
                </div>

                {/* 开启新对话按钮 */}
                <div style={{padding: '5px', borderBottom: '1px solid #e8e8e8'}}>
                    <Button
                        icon={<MessageOutlined size={40}/>}
                        size="large"
                        type="text"
                        style={{
                            width: '100%',
                            transition: 'background-color 0.3s',
                        }}
                        onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#e6f7ff'}
                        onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
                        onClick={() => setNewConversationModalVisible(true)}
                    >
                        {!collapsed && '开启新对话'}
                    </Button>
                    {collapsed && (
                        <Button
                            icon={<MenuUnfoldOutlined size={40}/>}
                            onClick={() => setCollapsed(false)}
                            size="large"
                            type="text"
                            style={{
                                marginTop: '10px',
                                width: '100%',
                                transition: 'background-color 0.3s',
                            }}
                            onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#e6f7ff'}
                            onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
                        />
                    )}
                </div>

                {/* 对话列表 */}
                {!collapsed && (
                    <div
                        style={{
                            borderRight: 'none',
                            height: 'calc(100vh - 170px)',
                            overflowY: 'auto',
                            backgroundColor: '#f9fbff',
                        }}
                    >
                        <Menu
                            mode="inline"
                            items={items}
                            selectedKeys={[conversationUuid || '']}
                            style={{
                                borderRight: 'none',
                                backgroundColor: '#f9fbff',
                            }}
                            theme="light"
                        />
                        {conversations.total > pagination.pageSize && (
                            <div style={{ padding: '8px', textAlign: 'center' }}>
                                <Button
                                    type="link"
                                    onClick={() => setPagination(prev => ({
                                        ...prev,
                                        pageSize: prev.pageSize + 20
                                    }))}
                                    loading={loading}
                                >
                                    加载更多
                                </Button>
                            </div>
                        )}
                    </div>
                )}

                <div style={{padding: '10px', position: "absolute",  bottom: '5px', width: '100%', display: 'none'}}>
                    <Dropdown
                        arrow
                        overlay={(
                            <Menu style={{width:'120px'}}>
                                <Menu.Item
                                    key="setting"
                                    onClick={() => {
                                    }}
                                >
                                    <SettingOutlined style={{ marginRight: '5px' }} /> 系统设置
                                </Menu.Item>
                                <Menu.Item
                                    key="contract"
                                >
                                    <MailOutlined style={{ marginRight: '5px' }} /> 联系我们
                                </Menu.Item>
                                <Menu.Item
                                    key="logout"
                                    onClick={() => {

                                    }}
                                >
                                    <LogoutOutlined style={{ marginRight: '5px' }} /> 退出登录
                                </Menu.Item>
                            </Menu>
                        )}
                    >
                        <Button
                            icon={<UserOutlined />}
                            size="large"
                            type="text"
                            style={{
                                width: '100%',
                                transition: 'background-color 0.3s',
                            }}
                        >{!collapsed && '个人信息'}</Button>
                    </Dropdown>
                </div>
            </Sider>

            {/* 主内容区域 */}
            <Layout style={{backgroundColor: 'white' }}>
                <Content style={{ height: 'calc(100vh - 80px)', width: '100%' }}>
                    {conversationUuid && <EmulatorComponent uuid={conversationUuid} />}
                </Content>
            </Layout>

            {/* 重命名模态框 */}
            <Modal
                title="重命名对话"
                open={renameModalVisible}
                onOk={() => {
                    if (renamingConversationUuid && newName.trim()) {
                        conversationDispatch.updateConversationInfo(renamingConversationUuid, {name: newName});
                        setRenameModalVisible(false);
                    } else {
                        message.error('名称不能为空');
                    }
                }}
                onCancel={() => setRenameModalVisible(false)}
                okText="确定"
                cancelText="取消"
            >
                <input
                    type="text"
                    value={newName}
                    onChange={(e) => setNewName(e.target.value)}
                    style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #d9d9d9' }}
                    placeholder="请输入新名称"
                />
            </Modal>

            {/* 智能体新会话模态框 */}
            <Modal
                title="选择智能体开启新对话"
                open={newConversationModalVisible}
                onCancel={() => setNewConversationModalVisible(false)}
                footer={null}
            >
                <div
                    style={{
                        height: '60vh',
                        overflowY: 'auto',
                    }}
                >
                    <List
                        dataSource={agents.items}
                        renderItem={item => (
                            <List.Item title={item.name} onClick={() => handleNewConversation(item)} >
                                <List.Item.Meta
                                    avatar={<Avatar src={`${import.meta.env.VITE_API_BASE_URL}${item.cover_image}`}/>}
                                    title={item.name}
                                />
                            </List.Item>
                        )}
                    />
                </div>
            </Modal>
        </Layout>
    );
};

export default AgentChatPage;