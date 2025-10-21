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
      formData.append('resource_type', 'textbook'); // 默认为教材
      formData.append('course_id', courseId.toString());
      formData.append('sort_order', '1'); // 默认排序为1
      formData.append('status', '1'); // 默认状态为启用
      formData.append('file', file);
      // 不添加description，默认为空

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
      >
        <Form.Item
          name="title"
          label="资源标题"
          rules={[{ required: true, message: '请输入资源标题' }]}
        >
          <Input placeholder="请输入资源标题" />
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