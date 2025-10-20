import React, { useState, useEffect } from 'react';
import { Modal, Form, Select, Input, Button, message } from 'antd';
import { courseApi, Course } from '../../api/course';

interface Grade {
  id: number;
  name: string;
  code: string;
  status: number;
}

interface CourseAgentMigrateComponentProps {
  visible: boolean;
  onCancel: () => void;
  onSuccess: () => void;
  agentUuid: string;
  agentName?: string;
}

const CourseAgentMigrateComponent: React.FC<CourseAgentMigrateComponentProps> = ({
  visible,
  onCancel,
  onSuccess,
  agentUuid,
  agentName
}) => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [grades, setGrades] = useState<Grade[]>([]);
  const [courses, setCourses] = useState<Course[]>([]);
  const [gradesLoading, setGradesLoading] = useState(false);
  const [coursesLoading, setCoursesLoading] = useState(false);
  const [selectedGradeId, setSelectedGradeId] = useState<number | undefined>();

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

  // 根据年级获取课程列表
  const fetchCoursesByGrade = async (gradeId: number) => {
    try {
      setCoursesLoading(true);
      const response = await courseApi.getCourseList({
        grade_id: gradeId,
        status: 1, // 只获取启用的课程
        limit: 1000 // 获取所有课程
      });
      if (response.code === 200) {
        setCourses(response.data.items || []);
      } else {
        message.error('获取课程列表失败');
      }
    } catch (error) {
      console.error('获取课程列表失败:', error);
      message.error('获取课程列表失败');
    } finally {
      setCoursesLoading(false);
    }
  };

  // 处理年级选择变化
  const handleGradeChange = (gradeId: number) => {
    setSelectedGradeId(gradeId);
    // 清空课程选择
    form.setFieldsValue({ courseId: undefined });
    setCourses([]);
    
    if (gradeId) {
      fetchCoursesByGrade(gradeId);
    }
  };

  useEffect(() => {
    if (visible) {
      fetchGrades();
      
      // 设置默认标题
      if (agentName) {
        form.setFieldsValue({
          title: agentName
        });
      }
    }
  }, [visible, agentName, form]);

  // 处理迁移提交
  const handleSubmit = async (values: any) => {
    try {
      setLoading(true);
      
      // 调用迁移API
      const result = await courseApi.migrateAgentToCourse({
        agent_uuid: agentUuid,
        course_id: values.courseId,
        title: values.title,
        description: values.description
      });
      
      if (result.code === 200) {
        message.success('智能体迁移成功！');
        form.resetFields();
        onSuccess();
      } else {
        message.error(result.message || '迁移失败');
      }
    } catch (error: any) {
      console.error('迁移失败:', error);
      const errorMessage = error.response?.data?.message || error.message || '迁移失败，请重试';
      message.error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  // 处理取消
  const handleCancel = () => {
    form.resetFields();
    setSelectedGradeId(undefined);
    setCourses([]);
    onCancel();
  };

  return (
    <Modal
      title="迁移智能体到课程"
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
        className="mt-4"
      >
        <Form.Item
          label="选择年级"
          name="gradeId"
          rules={[{ required: true, message: '请选择年级' }]}
        >
          <Select
            placeholder="请选择年级"
            loading={gradesLoading}
            onChange={handleGradeChange}
            showSearch
            filterOption={(input, option) =>
              (option?.label ?? '').toLowerCase().includes(input.toLowerCase())
            }
            options={grades.map(grade => ({
              value: grade.id,
              label: grade.name
            }))}
          />
        </Form.Item>

        <Form.Item
          label="选择目标课程"
          name="courseId"
          rules={[{ required: true, message: '请选择要迁移到的课程' }]}
        >
          <Select
            placeholder={selectedGradeId ? "请选择课程" : "请先选择年级"}
            loading={coursesLoading}
            disabled={!selectedGradeId}
            showSearch
            filterOption={(input, option) =>
              (option?.label ?? '').toLowerCase().includes(input.toLowerCase())
            }
            options={courses.map(course => ({
              value: course.id,
              label: course.title
            }))}
          />
        </Form.Item>

        <Form.Item
          label="在课程中显示的标题"
          name="title"
          rules={[{ required: true, message: '请输入标题' }]}
        >
          <Input placeholder="请输入在课程中显示的标题" />
        </Form.Item>

        <Form.Item
          label="描述"
          name="description"
        >
          <Input.TextArea
            placeholder="请输入描述（可选）"
            rows={3}
            maxLength={500}
            showCount
          />
        </Form.Item>

        <Form.Item className="mb-0 text-right">
          <Button onClick={handleCancel} className="mr-2">
            取消
          </Button>
          <Button 
            type="primary" 
            htmlType="submit" 
            loading={loading}
            className="bg-[#7F56D9] hover:bg-[#6941C6]"
          >
            确认迁移
          </Button>
        </Form.Item>
      </Form>
    </Modal>
  );
};

export default CourseAgentMigrateComponent;