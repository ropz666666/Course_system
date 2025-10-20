import React, { useState } from 'react';
import { 
  Modal, 
  Form, 
  Input, 
  Select, 
  Upload, 
  Button, 
  message, 
  Space,
  Typography 
} from 'antd';
import { UploadOutlined, InboxOutlined } from '@ant-design/icons';
import type { UploadFile, UploadProps } from 'antd';
import { courseApi } from '../../api/course';

const { Option } = Select;
const { TextArea } = Input;
const { Dragger } = Upload;
const { Text } = Typography;

interface CreateCourseResourceComponentProps {
  courseId: number;
  onCancel: () => void;
  onSuccess: () => void;
}

interface CreateCourseResourceFormData {
  title: string;
  resource_type: string;
  description?: string;
  sort_order: number;
  status: number;
}

const CreateCourseResourceComponent: React.FC<CreateCourseResourceComponentProps> = ({
  courseId,
  onCancel,
  onSuccess,
}) => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [fileList, setFileList] = useState<UploadFile[]>([]);

  // 处理文件上传
  const handleUpload: UploadProps['customRequest'] = async (options) => {
    const { file, onSuccess: onUploadSuccess, onError } = options;
    
    try {
      // 直接标记为成功，实际上传将在表单提交时进行
      if (onUploadSuccess) {
        onUploadSuccess({
          url: `temp-${Date.now()}`,
          name: (file as File).name,
          size: (file as File).size,
          type: (file as File).type,
        });
      }
    } catch (error) {
      console.error('文件处理失败:', error);
      if (onError) {
        onError(new Error('文件处理失败'));
      }
    }
  };

  // 处理文件列表变化
  const handleFileChange: UploadProps['onChange'] = (info) => {
    setFileList(info.fileList);
  };

  // 处理表单提交
  const handleSubmit = async (values: CreateCourseResourceFormData) => {
    if (fileList.length === 0) {
      message.error('请选择要上传的文件');
      return;
    }

    try {
      setLoading(true);
      
      const uploadedFile = fileList[0];
      const file = uploadedFile.originFileObj;
      
      if (!file) {
        message.error('文件信息不完整');
        return;
      }

      // 创建FormData对象
      const formData = new FormData();
      formData.append('title', values.title);
      formData.append('resource_type', values.resource_type);
      formData.append('course_id', courseId.toString());
      formData.append('sort_order', values.sort_order.toString());
      formData.append('status', values.status.toString());
      formData.append('file', file);
      
      if (values.description) {
        formData.append('description', values.description);
      }

      // 调用创建课程资源API
      const response = await courseApi.createCourseResource(formData);
      console.log('API Response:', response);
      
      if (response.code === 200) {
        message.success('课程资源创建成功');
        form.resetFields();
        setFileList([]);
        onSuccess();
      } else {
        message.error(response.message || '创建失败');
      }
    } catch (error) {
      console.error('创建课程资源失败:', error);
      message.error('创建课程资源失败');
    } finally {
      setLoading(false);
    }
  };

  // 处理取消
  const handleCancel = () => {
    form.resetFields();
    setFileList([]);
    onCancel();
  };

  return (
    <div>
      <Form
        form={form}
        layout="vertical"
        onFinish={handleSubmit}
        initialValues={{
          resource_type: 'textbook',
          sort_order: 1,
          status: 1,
        }}
      >
        <Form.Item
          name="title"
          label="资源标题"
          rules={[{ required: true, message: '请输入资源标题' }]}
        >
          <Input placeholder="请输入资源标题" />
        </Form.Item>

        <Form.Item
          name="resource_type"
          label="资源类型"
          rules={[{ required: true, message: '请选择资源类型' }]}
        >
          <Select placeholder="请选择资源类型">
            <Option value="textbook">教材</Option>
            <Option value="outline">大纲</Option>
            <Option value="lesson_plan">教案</Option>
            <Option value="ppt">课件</Option>
            <Option value="video">视频</Option>
          </Select>
        </Form.Item>

        <Form.Item
          name="description"
          label="资源描述"
        >
          <TextArea 
            rows={3} 
            placeholder="请输入资源描述（可选）" 
            maxLength={500}
            showCount
          />
        </Form.Item>

        <Form.Item
          label="上传文件"
          required
        >
          <Dragger
            fileList={fileList}
            onChange={handleFileChange}
            customRequest={handleUpload}
            maxCount={1}
            beforeUpload={(file) => {
              // 文件大小限制：100MB
              const isLt100M = file.size / 1024 / 1024 < 100;
              if (!isLt100M) {
                message.error('文件大小不能超过100MB');
                return false;
              }
              
              // 文件类型验证
              const allowedExtensions = ['pdf', 'doc', 'docx', 'ppt', 'pptx', 'txt', 'md', 'jpg', 'jpeg', 'png', 'gif', 'mp4', 'avi', 'mov'];
              const fileExtension = file.name.split('.').pop()?.toLowerCase();
              if (!fileExtension || !allowedExtensions.includes(fileExtension)) {
                message.error(`不支持的文件类型 '${fileExtension}'。支持的文件类型：${allowedExtensions.join(', ')}`);
                return false;
              }
              
              return true;
            }}
          >
            <p className="ant-upload-drag-icon">
              <InboxOutlined />
            </p>
            <p className="ant-upload-text">点击或拖拽文件到此区域上传</p>
            <p className="ant-upload-hint">
              支持单个文件上传，文件大小不超过100MB
            </p>
          </Dragger>
        </Form.Item>

        <Form.Item
          name="sort_order"
          label="排序"
          rules={[{ required: true, message: '请输入排序值' }]}
        >
          <Input 
            type="number" 
            placeholder="请输入排序值" 
            min={1}
          />
        </Form.Item>

        <Form.Item
          name="status"
          label="状态"
          rules={[{ required: true, message: '请选择状态' }]}
        >
          <Select placeholder="请选择状态">
            <Option value={1}>启用</Option>
            <Option value={0}>禁用</Option>
          </Select>
        </Form.Item>

        <Form.Item>
          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '8px' }}>
            <Button onClick={handleCancel}>
              取消
            </Button>
            <Button type="primary" htmlType="submit" loading={loading}>
              上传资源
            </Button>
          </div>
        </Form.Item>
      </Form>
    </div>
  );
};

export default CreateCourseResourceComponent;