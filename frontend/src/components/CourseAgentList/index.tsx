import React, { useState, useEffect } from 'react';
import { 
  Card, 
  List, 
  Button, 
  Spin, 
  message, 
  Empty, 
  Tag, 
  Typography, 
  Space, 
  Avatar,
  Popconfirm,
  Modal,
  Form,
  Input
} from 'antd';
import { 
  RobotOutlined,
  DeleteOutlined,
  EditOutlined,
  UserOutlined,
  CalendarOutlined
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { courseApi, CourseAgent, UpdateCourseAgentParam } from '../../api/course';
import './index.css';

const { Title, Text } = Typography;

interface CourseAgentListProps {
  courseId: number;
}

const CourseAgentList: React.FC<CourseAgentListProps> = ({ courseId }) => {
  const [agents, setAgents] = useState<CourseAgent[]>([]);
  const [loading, setLoading] = useState(true);
  const [editModalVisible, setEditModalVisible] = useState(false);
  const [editingAgent, setEditingAgent] = useState<CourseAgent | null>(null);
  const [form] = Form.useForm();
  const navigate = useNavigate();

  useEffect(() => {
    fetchCourseAgents();
  }, [courseId]);

  const fetchCourseAgents = async () => {
    try {
      setLoading(true);
      const response = await courseApi.getCourseAgents(courseId);
      if (response.code === 200) {
        setAgents(response.data || []);
      } else {
        message.error('获取课程智能体失败');
      }
    } catch (error) {
      console.error('获取课程智能体失败:', error);
      message.error('获取课程智能体失败');
    } finally {
      setLoading(false);
    }
  };

  const handleRemoveAgent = async (agent: CourseAgent) => {
    try {
      const response = await courseApi.removeAgentFromCourse(courseId, agent.agent_uuid);
      if (response.code === 200) {
        message.success('移除智能体成功');
        fetchCourseAgents(); // 重新获取列表
      } else {
        message.error('移除智能体失败');
      }
    } catch (error) {
      console.error('移除智能体失败:', error);
      message.error('移除智能体失败');
    }
  };

  const handleEditAgent = (agent: CourseAgent) => {
    setEditingAgent(agent);
    form.setFieldsValue({
      title: agent.title,
      description: agent.description
    });
    setEditModalVisible(true);
  };

  const handleEditSubmit = async () => {
    if (!editingAgent) return;

    try {
      const values = await form.validateFields();
      const updateData: UpdateCourseAgentParam = {
        title: values.title,
        description: values.description
      };

      const response = await courseApi.updateCourseAgent(courseId, editingAgent.agent_uuid, updateData);
      console.log('更新智能体信息响应:', response);
      if (response.code === 200) {
        message.success('更新智能体信息成功');
        setEditModalVisible(false);
        setEditingAgent(null);
        form.resetFields();
        fetchCourseAgents(); // 重新获取列表
      } else {
        message.error('更新智能体信息失败');
      }
    } catch (error) {
      console.error('更新智能体信息失败:', error);
      message.error('更新智能体信息失败');
    }
  };

  const handleEditCancel = () => {
    setEditModalVisible(false);
    setEditingAgent(null);
    form.resetFields();
  };

  const handleAgentClick = (agent: CourseAgent) => {
    if (agent.agent_uuid) {
      navigate(`/agent/display/${agent.agent_uuid}`);
    }
  };

  const getStatusTag = (status: number) => {
    switch (status) {
      case 1:
        return <Tag color="green">启用</Tag>;
      case 0:
        return <Tag color="red">禁用</Tag>;
      default:
        return <Tag>未知</Tag>;
    }
  };

  const getAgentTypeTag = (type: string) => {
    const typeMap: { [key: string]: { color: string; text: string } } = {
      'tool': { color: 'blue', text: '工具型' },
      'chat': { color: 'green', text: '对话型' },
      'workflow': { color: 'purple', text: '工作流' }
    };
    const config = typeMap[type] || { color: 'default', text: type };
    return <Tag color={config.color}>{config.text}</Tag>;
  };

  return (
    <Card 
      title={
        <Space>
          <RobotOutlined />
          <span>课程智能体</span>
          <Tag color="blue">{agents.length}</Tag>
        </Space>
      }
      bordered={false}
      className="course-agents-card"
    >
      <Spin spinning={loading}>
        {agents.length === 0 ? (
          <Empty 
            description="暂无课程智能体" 
            image={Empty.PRESENTED_IMAGE_SIMPLE}
          />
        ) : (
          <List
            itemLayout="horizontal"
            dataSource={agents}
            renderItem={(agent) => (
              <List.Item
                className="agent-list-item"
                onClick={() => handleAgentClick(agent)}
                style={{ cursor: 'pointer' }}
                actions={[
                  <Button
                    type="text"
                    icon={<EditOutlined />}
                    onClick={(e) => {
                      e.stopPropagation();
                      handleEditAgent(agent);
                    }}
                    size="small"
                  >
                    编辑
                  </Button>,
                  <Popconfirm
                    title="确定要从课程中移除这个智能体吗？"
                    onConfirm={(e) => {
                      e?.stopPropagation();
                      handleRemoveAgent(agent);
                    }}
                    okText="确定"
                    cancelText="取消"
                  >
                    <Button
                      type="text"
                      danger
                      icon={<DeleteOutlined />}
                      size="small"
                      onClick={(e) => e.stopPropagation()}
                    >
                      移除
                    </Button>
                  </Popconfirm>
                ]}
              >
                <List.Item.Meta
                  avatar={
                    <Avatar 
                      src={agent.agent?.cover_image}
                      icon={<RobotOutlined />} 
                      style={{ backgroundColor: '#1890ff' }}
                      size="large"
                    />
                  }
                  title={
                    <Space>
                      <Text strong>{agent.title}</Text>
                      {/* {agent.agent && getAgentTypeTag(agent.agent.type)}
                      {getStatusTag(agent.status)} */}
                    </Space>
                  }
                  description={
                    <Space direction="vertical" size="small">
                      {agent.description && (
                        <Text type="secondary">{agent.description}</Text>
                      )}
                      <Space size="large">
                        {/* {agent.agent && (
                          <Text type="secondary">
                            原名称: {agent.agent.name}
                          </Text>
                        )} */}
                        {agent.migrator && (
                          <Text type="secondary">
                            <UserOutlined /> 迁移者: {agent.migrator.username}
                          </Text>
                        )}
                        <Text type="secondary">
                          <CalendarOutlined /> 迁移时间: {new Date(agent.created_time).toLocaleDateString()}
                        </Text>
                      </Space>
                    </Space>
                  }
                />
              </List.Item>
            )}
          />
        )}
      </Spin>

      {/* 编辑智能体信息模态框 */}
      <Modal
        title="编辑智能体信息"
        open={editModalVisible}
        onOk={handleEditSubmit}
        onCancel={handleEditCancel}
        okText="保存"
        cancelText="取消"
        width={600}
      >
        <Form
          form={form}
          layout="vertical"
          preserve={false}
        >
          <Form.Item
            name="title"
            label="在课程中显示的标题"
            rules={[{ required: true, message: '请输入标题' }]}
          >
            <Input placeholder="请输入在课程中显示的标题" />
          </Form.Item>
          
          <Form.Item
            name="description"
            label="在课程中显示的描述"
          >
            <Input.TextArea 
              rows={4} 
              placeholder="请输入在课程中显示的描述（可选）" 
            />
          </Form.Item>
        </Form>
      </Modal>
    </Card>
  );
};

export default CourseAgentList;