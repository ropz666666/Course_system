import React, { useState, useEffect } from 'react';
import { Modal, Form, Input, Select, Upload, Button, message, Spin } from 'antd';
import { PlusOutlined, UploadOutlined } from '@ant-design/icons';
import { courseApi } from '../../api/course';
import type { UploadFile } from 'antd/es/upload/interface';

const { TextArea } = Input;
const { Option } = Select;

interface Grade {
  id: number;
  name: string;
  code: string;
  sort_order: number;
  status: number;
}

interface Subject {
  id: number;
  name: string;
  code: string;
  description?: string;
  sort_order: number;
  status: number;
}

interface CreateCourseComponentProps {
  visible: boolean;
  onCancel: () => void;
  onSuccess: () => void;
}

interface CreateCourseFormData {
  title: string;
  description?: string;
  grade_id: number;
  subject_id: number;
  cover_image?: string;
  sort_order: number;
  status: number;
}

const CreateCourseComponent: React.FC<CreateCourseComponentProps> = ({
  visible,
  onCancel,
  onSuccess,
}) => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [grades, setGrades] = useState<Grade[]>([]);
  const [subjects, setSubjects] = useState<Subject[]>([]);
  const [gradesLoading, setGradesLoading] = useState(false);
  const [subjectsLoading, setSubjectsLoading] = useState(false);
  const [fileList, setFileList] = useState<UploadFile[]>([]);

  // 获取年级列表
  const fetchGrades = async () => {
    try {
      setGradesLoading(true);
      const response = await courseApi.getGradeList();
      if (response.code === 200) {
        setGrades(response.data.items || []);
      } else {
        message.error('获取年级列表失败');
      }
    } catch (error) {
      console.error('获取年级列表失败:', error);
      message.error('获取年级列表失败');
    } finally {
      setGradesLoading(false);
    }
  };

  // 获取科目列表
  const fetchSubjects = async () => {
    try {
      setSubjectsLoading(true);
      const response = await courseApi.getSubjectList();
      if (response.code === 200) {
        setSubjects(response.data.items || []);
      } else {
        console.error('获取科目列表失败 response:', response);
        message.error('获取科目列表失败');
      }
    } catch (error) {
      console.error('获取科目列表失败:', error);
      message.error('获取科目列表失败');
    } finally {
      setSubjectsLoading(false);
    }
  };

  useEffect(() => {
    if (visible) {
      fetchGrades();
      fetchSubjects();
    }
  }, [visible]);

  // 处理表单提交
  const handleSubmit = async (values: CreateCourseFormData) => {
    try {
      setLoading(true);
      
      // 准备提交数据
      const submitData = {
        ...values,
        cover_image: fileList.length > 0 ? fileList[0].url || fileList[0].response?.url : undefined,
      };

      const response = await courseApi.createCourse(submitData);
      console.log('创建课程响应:', response);
      if (response.code === 200) {
        message.success('课程创建成功');
        form.resetFields();
        setFileList([]);
        onSuccess();
      } else {
        message.error(response);
      }
    } catch (error) {
      console.error('创建课程失败:', error);
      message.error('创建课程失败');
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

  // 处理文件上传
  const handleUploadChange = ({ fileList: newFileList }: { fileList: UploadFile[] }) => {
    setFileList(newFileList);
  };

  // 上传前的检查
  const beforeUpload = (file: File) => {
    const isImage = file.type.startsWith('image/');
    if (!isImage) {
      message.error('只能上传图片文件!');
      return false;
    }
    const isLt2M = file.size / 1024 / 1024 < 2;
    if (!isLt2M) {
      message.error('图片大小不能超过 2MB!');
      return false;
    }
    return true;
  };

  return (
    <Modal
      title="创建课程"
      open={visible}
      onCancel={handleCancel}
      footer={null}
      width={600}
      destroyOnClose
    >
      <Form
        form={form}
        layout="vertical"
        onFinish={handleSubmit}
        initialValues={{
          status: 1,
          sort_order: 1,
        }}
      >
        <Form.Item
          name="title"
          label="课程标题"
          rules={[
            { required: true, message: '请输入课程标题' },
            { max: 255, message: '课程标题不能超过255个字符' },
          ]}
        >
          <Input placeholder="请输入课程标题" />
        </Form.Item>

        <Form.Item
          name="description"
          label="课程描述"
          rules={[{ max: 1000, message: '课程描述不能超过1000个字符' }]}
        >
          <TextArea
            rows={4}
            placeholder="请输入课程描述"
            showCount
            maxLength={1000}
          />
        </Form.Item>

        <Form.Item
          name="grade_id"
          label="年级"
          rules={[{ required: true, message: '请选择年级' }]}
        >
          <Select
            placeholder="请选择年级"
            loading={gradesLoading}
            showSearch
            filterOption={(input, option) =>
              (option?.children as unknown as string)?.toLowerCase().includes(input.toLowerCase())
            }
          >
            {grades.map((grade) => (
              <Option key={grade.id} value={grade.id}>
                {grade.name}
              </Option>
            ))}
          </Select>
        </Form.Item>

        <Form.Item
          name="subject_id"
          label="科目"
          rules={[{ required: true, message: '请选择科目' }]}
        >
          <Select
            placeholder="请选择科目"
            loading={subjectsLoading}
            showSearch
            filterOption={(input, option) =>
              (option?.children as unknown as string)?.toLowerCase().includes(input.toLowerCase())
            }
          >
            {subjects.map((subject) => (
              <Option key={subject.id} value={subject.id}>
                {subject.name}
              </Option>
            ))}
          </Select>
        </Form.Item>

        <Form.Item
          name="cover_image"
          label="封面图片"
        >
          <Upload
            listType="picture-card"
            fileList={fileList}
            onChange={handleUploadChange}
            beforeUpload={beforeUpload}
            maxCount={1}
            accept="image/*"
          >
            {fileList.length < 1 && (
              <div>
                <PlusOutlined />
                <div style={{ marginTop: 8 }}>上传封面</div>
              </div>
            )}
          </Upload>
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
              创建课程
            </Button>
          </div>
        </Form.Item>
      </Form>
    </Modal>
  );
};

export default CreateCourseComponent;