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
  Divider,
  Row,
  Col,
  Descriptions,
  Avatar,
  Modal
} from 'antd';
import { 
  DownloadOutlined, 
  FileTextOutlined, 
  ArrowLeftOutlined,
  BookOutlined,
  UserOutlined,
  CalendarOutlined,
  EyeOutlined,
  UploadOutlined
} from '@ant-design/icons';
import { courseApi, Course, CourseResource } from '../../api/course';
import { getUserInfo } from '../../api/user';
import { UserInfo } from '../../types/userType';
import CreateCourseResourceComponent from '../CreateCourseResourceComponent';
import CourseAgentList from '../CourseAgentList';
import './index.css';

const { Title, Text, Paragraph } = Typography;

interface CourseDetailComponentProps {
  courseId: number;
  onBack: () => void;
}

const CourseDetailComponent: React.FC<CourseDetailComponentProps> = ({ courseId, onBack }) => {
  const [course, setCourse] = useState<Course | null>(null);
  const [resources, setResources] = useState<CourseResource[]>([]);
  const [loading, setLoading] = useState(true);
  const [resourcesLoading, setResourcesLoading] = useState(false);
  const [userInfo, setUserInfo] = useState<UserInfo | null>(null);
  const [isUploadModalVisible, setIsUploadModalVisible] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        
        // 获取课程详情
        const courseResponse = await courseApi.getCourseDetail(courseId);
        if (courseResponse.code === 200) {
          setCourse(courseResponse.data);
        }  
        // 获取用户信息
        const userResponse = await getUserInfo();
        setUserInfo(userResponse);
        
        // 获取课程资源
        await fetchCourseResources();
      } catch (error) {
        console.error('获取数据失败:', error);
        message.error('获取数据失败');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [courseId]);

  const fetchCourseDetail = async () => {
    try {
      setLoading(true);
      const response = await courseApi.getCourseDetail(courseId);
      if (response.code === 200) {
        setCourse(response.data);
      } else {
        message.error('获取课程详情失败');
      }
    } catch (error) {
      console.error('获取课程详情失败:', error);
      message.error('获取课程详情失败');
    } finally {
      setLoading(false);
    }
  };

  const fetchCourseResources = async () => {
    try {
      setResourcesLoading(true);
      const response = await courseApi.getCourseResources({ course_id: courseId });
      if (response.code === 200) {
        setResources(response.data.items || []);
      } else {
        message.error('获取课程资源失败');
      }
    } catch (error) {
      console.error('获取课程资源失败:', error);
      message.error('获取课程资源失败');
    } finally {
      setResourcesLoading(false);
    }
  };

  // 处理上传成功后的回调
  const handleUploadSuccess = () => {
    setIsUploadModalVisible(false);
    fetchCourseResources(); // 重新获取资源列表
    message.success('课程资源上传成功！');
  };

  // 显示上传模态框
  const showUploadModal = () => {
    setIsUploadModalVisible(true);
  };

  // 关闭上传模态框
  const handleUploadCancel = () => {
    setIsUploadModalVisible(false);
  };

  const handleDownload = async (resource: CourseResource) => {
    try {
      const blob = await courseApi.downloadCourseResource(resource.id);
      console.log("blob", blob)
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
     
      link.href = url;
      link.download = resource.file_name || resource.title;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      message.success('下载成功');
    } catch (error) {
      console.error('下载失败:', error);
      message.error('下载失败');
    }
  };

  const handlePreview = async (resource: CourseResource) => {
    try {
      const blob = await courseApi.previewCourseResource(resource.id);
      const url = window.URL.createObjectURL(blob);
      
      // 根据文件类型决定预览方式
      const fileType = resource.file_type.toLowerCase();
      
      if (fileType.includes('image')) {
        // 图片预览
        Modal.info({
          title: `预览 - ${resource.title}`,
          content: (
            <div style={{ textAlign: 'center' }}>
              <img 
                src={url} 
                alt={resource.title}
                style={{ maxWidth: '100%', maxHeight: '500px' }}
              />
            </div>
          ),
          width: 800,
          onOk: () => window.URL.revokeObjectURL(url)
        });
      } else if (fileType.includes('pdf')) {
        // PDF预览
        window.open(url, '_blank');
      } else if (fileType.includes('text') || fileType.includes('json') || fileType.includes('xml')) {
        // 文本文件预览
        const text = await blob.text();
        Modal.info({
          title: `预览 - ${resource.title}`,
          content: (
            <div>
              <pre style={{ 
                maxHeight: '400px', 
                overflow: 'auto', 
                backgroundColor: '#f5f5f5', 
                padding: '16px',
                borderRadius: '4px'
              }}>
                {text}
              </pre>
            </div>
          ),
          width: 800,
          onOk: () => window.URL.revokeObjectURL(url)
        });
      } else {
        // 其他文件类型在新窗口打开
        window.open(url, '_blank');
      }
    } catch (error: any) {
      console.error('预览失败:', error);
      if (error.response?.status === 415) {
        message.warning('该文件类型不支持预览，请下载后查看');
      } else {
        message.error('预览失败');
      }
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getResourceTypeTag = (type: string) => {
    const typeMap: { [key: string]: { color: string; text: string } } = {
      textbook: { color: 'blue', text: '教材' },
      outline: { color: 'green', text: '大纲' },
      lesson_plan: { color: 'orange', text: '教案' },
      ppt: { color: 'purple', text: '课件' },
      video: { color: 'red', text: '视频' }
    };
    const config = typeMap[type] || { color: 'default', text: type };
    return <Tag color={config.color}>{config.text}</Tag>;
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

  if (loading) {
    return (
      <div className="course-detail-loading">
        <Spin size="large" />
      </div>
    );
  }

  if (!course) {
    return (
      <div className="course-detail-error">
        <Empty description="课程不存在" />
        <Button type="primary" onClick={onBack} style={{ marginTop: 16 }}>
          返回课程列表
        </Button>
      </div>
    );
  }

  return (
    <div className="course-detail-container">
      {/* 头部导航 */}
      <div className="course-detail-header">
        <Button 
          type="text" 
          icon={<ArrowLeftOutlined />} 
          onClick={onBack}
          className="back-button"
        >
          返回课程列表
        </Button>
      </div>

     

      <Divider />

      {/* 课程智能体列表 */}
      <CourseAgentList courseId={courseId} />

      <Divider />

      {/* 课程资源列表 */}
      <Card 
        title={
          <Space>
            <FileTextOutlined />
            <span>课程资源</span>
            <Tag color="blue">{resources.length}</Tag>
          </Space>
        }
        extra={
          userInfo?.is_superuser && (
            <Button
              type="primary"
              icon={<UploadOutlined />}
              onClick={showUploadModal}
            >
              上传课程资源
            </Button>
          )
        }
        bordered={false}
        className="course-resources-card"
      >
        <Spin spinning={resourcesLoading}>
          {resources.length === 0 ? (
            <Empty 
              description="暂无课程资源" 
              image={Empty.PRESENTED_IMAGE_SIMPLE}
            />
          ) : (
            <List
              itemLayout="horizontal"
              dataSource={resources}
              renderItem={(resource) => (
                <List.Item
                  className="resource-list-item"
                  actions={[
                    <Button
                      type="primary"
                      icon={<DownloadOutlined />}
                      onClick={() => handleDownload(resource)}
                      size="small"
                    >
                      下载
                    </Button>,
                    <Button
                      type="text"
                      icon={<EyeOutlined />}
                      onClick={() => handlePreview(resource)}
                      size="small"
                    >
                      预览
                    </Button>
                  ]}
                >
                  <List.Item.Meta
                    avatar={
                      <Avatar 
                        icon={<FileTextOutlined />} 
                        style={{ backgroundColor: '#1890ff' }}
                      />
                    }
                    title={
                      <Space>
                        <Text strong>{resource.title}</Text>
                        {getResourceTypeTag(resource.resource_type)}
                        {getStatusTag(resource.status)}
                      </Space>
                    }
                    description={
                      <Space direction="vertical" size="small">
                        {resource.description && (
                          <Text type="secondary">{resource.description}</Text>
                        )}
                        <Space size="large">
                          {resource.file_name && (
                            <Text type="secondary">
                              资源名: {resource.file_name}
                            </Text>
                          )}
                         
                          {resource.file_size && (
                            <Text type="secondary">
                              大小: {formatFileSize(resource.file_size)}
                            </Text>
                          )}
                          <Text type="secondary">
                            下载次数: {resource.download_count}
                          </Text>
                          <Text type="secondary">
                            上传时间: {new Date(resource.created_time).toLocaleDateString()}
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
      </Card>

      {/* 上传课程资源模态框 */}
      <Modal
        title="上传课程资源"
        open={isUploadModalVisible}
        onCancel={handleUploadCancel}
        footer={null}
        width={600}
        destroyOnClose
      >
        <CreateCourseResourceComponent
          courseId={courseId}
          onSuccess={handleUploadSuccess}
          onCancel={handleUploadCancel}
        />
      </Modal>
    </div>
  );
};

export default CourseDetailComponent;