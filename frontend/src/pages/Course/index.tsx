import React, { useState, useEffect } from 'react';
import { Layout, Menu, Card, List, Spin, message, Empty, Tag, Button, Modal, Dropdown } from 'antd';
import { BookOutlined, FileTextOutlined, DownloadOutlined, PlusOutlined, EditOutlined, DeleteOutlined, MoreOutlined } from '@ant-design/icons';
import type { MenuProps } from 'antd';
import { courseApi } from '../../api/course';
import CourseDetailComponent from '../../components/CourseDetailComponent';
import CreateCourseComponent from '../../components/CreateCourseComponent';
import { useUserSelector, useDispatchUser } from '../../hooks/user';
import './index.css';

const { Sider, Content } = Layout;

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

interface Course {
  id: number;
  title: string;
  description: string;
  teacher_uuid: string;
  grade_id: number;
  subject_id: number;
  cover_image?: string;
  status: number;
  sort_order: number;
  created_time: string;
  updated_time?: string;
  grade?: Grade;
  subject?: Subject;
  resources?: CourseResource[];
}

interface CourseResource {
  id: number;
  uuid: string;
  title: string;
  resource_type: string;
  course_id: number;
  upload_user_uuid: string;
  description?: string;
  file_name: string;
  file_path: string;
  file_size: number;
  file_type: string;
  download_count: number;
  status: number;
  sort_order: number;
  created_time: string;
  updated_time?: string;
}

const CoursePage: React.FC = () => {
  const [grades, setGrades] = useState<Grade[]>([]);
  const [courses, setCourses] = useState<Course[]>([]);
  const [selectedGradeId, setSelectedGradeId] = useState<number | null>(null);
  const [selectedCourseId, setSelectedCourseId] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);
  const [gradesLoading, setGradesLoading] = useState(true);
  const [createCourseVisible, setCreateCourseVisible] = useState(false);
  const [editCourseVisible, setEditCourseVisible] = useState(false);
  const [editingCourse, setEditingCourse] = useState<Course | null>(null);
  
  // 获取用户信息，检查是否为超级用户
  const userData = useUserSelector((state) => state.user.user);
  const { fetchUser } = useDispatchUser();
  


  // 获取年级列表
  useEffect(() => {
    const fetchGrades = async () => {
      try {
        setGradesLoading(true);
        const response = await courseApi.getGradeList();
        if (response.code === 200) {
          setGrades(response.data.items || []);
          // 默认选择第一个年级
          if (response.data.items && response.data.items.length > 0) {
            setSelectedGradeId(response.data.items[0].id);
          }
        } else {
          console.error('获取年级列表失败 response:', response);
          message.error('获取年级列表失败');
        }
      } catch (error) {
        console.error('获取年级列表失败:', error);
        message.error('获取年级列表失败');
      } finally {
        setGradesLoading(false);
      }
    };

    fetchGrades();
    // 获取用户信息
    fetchUser();
  }, [fetchUser]);

  // 根据选中的年级获取课程列表
  useEffect(() => {
    if (selectedGradeId) {
      fetchCourses(selectedGradeId);
    }
  }, [selectedGradeId]);

  const fetchCourses = async (gradeId: number) => {
    try {
      setLoading(true);
      const response = await courseApi.getCourseList({ grade_id: gradeId });
      if (response.code === 200) {
        setCourses(response.data.items || []);
      } else {
        console.error('获取课程列表失败:', response);
        message.error('获取课程列表失败');
      }
    } catch (error) {
      console.error('获取课程列表失败:', error);
      message.error('获取课程列表失败');
    } finally {
      setLoading(false);
    }
  };

  const handleGradeSelect = (gradeId: number) => {
    setSelectedGradeId(gradeId);
    setSelectedCourseId(null); // 重置选中的课程
  };

  const handleCourseSelect = (courseId: number) => {
    setSelectedCourseId(courseId);
  };

  const handleBackToCourseList = () => {
    setSelectedCourseId(null);
  };

  // 处理创建课程按钮点击
  const handleCreateCourse = () => {
    setCreateCourseVisible(true);
  };

  // 处理创建课程成功
  const handleCreateCourseSuccess = () => {
    setCreateCourseVisible(false);
    // 刷新当前年级的课程列表
    if (selectedGradeId) {
      fetchCourses(selectedGradeId);
    }
  };

  // 处理创建课程取消
  const handleCreateCourseCancel = () => {
    setCreateCourseVisible(false);
  };

  // 处理编辑课程
  const handleEditCourse = (course: Course) => {
    setEditingCourse(course);
    setEditCourseVisible(true);
  };

  // 处理编辑课程成功
  const handleEditCourseSuccess = () => {
    setEditCourseVisible(false);
    setEditingCourse(null);
    // 刷新当前年级的课程列表
    if (selectedGradeId) {
      fetchCourses(selectedGradeId);
    }
  };

  // 处理编辑课程取消
  const handleEditCourseCancel = () => {
    setEditCourseVisible(false);
    setEditingCourse(null);
  };

  // 处理删除课程
  const handleDeleteCourse = (course: Course) => {
    Modal.confirm({
      title: '确认删除',
      content: `确定要删除课程"${course.title}"吗？此操作不可撤销。`,
      okText: '确定',
      cancelText: '取消',
      okType: 'danger',
      onOk: async () => {
        try {
          const response = await courseApi.deleteCourse(course.id);
          if (response.code === 200) {
            message.success('删除课程成功');
            // 刷新当前年级的课程列表
            if (selectedGradeId) {
              fetchCourses(selectedGradeId);
            }
          } else {
            message.error(response.msg || '删除课程失败');
          }
        } catch (error) {
          console.error('删除课程失败:', error);
          message.error('删除课程失败');
        }
      }
    });
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

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const menuItems = grades.map(grade => ({
    key: grade.id.toString(),
    icon: <BookOutlined />,
    label: grade.name,
  }));

  // 如果选中了课程，显示课程详情页面
  if (selectedCourseId) {
    return (
      <CourseDetailComponent 
        courseId={selectedCourseId} 
        onBack={handleBackToCourseList}
      />
    );
  }

  return (
    <div className="course-page">
      <Layout style={{ minHeight: '100vh', background: '#f5f5f5' }}>
        <Sider width={250} theme="light" className="course-sidebar">
        
          <Spin spinning={gradesLoading}>
            <Menu
              mode="inline"
              selectedKeys={selectedGradeId ? [selectedGradeId.toString()] : []}
              items={menuItems}
              onSelect={({ key }) => handleGradeSelect(Number(key))}
              className="grade-menu"
            />
          </Spin>
        </Sider>
        
        <Content className="course-content">
          <div className="content-header">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <h2>
                {selectedGradeId && grades.find(g => g.id === selectedGradeId)?.name} 课程
              </h2>
              {/* 只有超级用户才能看到创建课程按钮 */}
              {userData?.is_superuser && (
                <Button 
                  type="primary" 
                  icon={<PlusOutlined />}
                  onClick={handleCreateCourse}
                >
                  创建课程
                </Button>
              )}
            </div>
          </div>
          
          <Spin spinning={loading}>
            {courses.length === 0 && !loading ? (
              <Empty description="暂无课程" />
            ) : (
              <List
                grid={{
                  gutter: 16,
                  xs: 1,
                  sm: 2,
                  md: 2,
                  lg: 3,
                  xl: 3,
                  xxl: 4,
                }}
                dataSource={courses}
                renderItem={(course) => {
                  // 创建超级用户菜单项
                  const menuItems: MenuProps['items'] = userData?.is_superuser ? [
                    {
                      key: 'edit',
                      label: '编辑课程',
                      icon: <EditOutlined />,
                      onClick: () => handleEditCourse(course),
                    },
                    {
                      key: 'delete',
                      label: '删除课程',
                      icon: <DeleteOutlined />,
                      danger: true,
                      onClick: () => handleDeleteCourse(course),
                    },
                  ] : [];

                  return (
                    <List.Item>
                      <Card
                        hoverable
                        className="course-card"
                        cover={
                          course.cover_image ? (
                            <img
                              alt={course.title}
                              src={course.cover_image}
                              className="course-cover"
                            />
                          ) : (
                            <div className="course-cover-placeholder">
                              <BookOutlined style={{ fontSize: 48, color: '#ccc' }} />
                            </div>
                          )
                        }
                        actions={[
                          <Button 
                            type="link" 
                            size="small"
                            onClick={() => handleCourseSelect(course.id)}
                          >
                            查看详情
                          </Button>
                        ]}
                      >
                        {/* 右上角菜单按钮 - 只有超级用户可见 */}
                        {userData?.is_superuser && (
                          <div className="course-card-menu">
                            <Dropdown
                              menu={{ items: menuItems }}
                              placement="bottomRight"
                              trigger={['click']}
                            >
                              <Button
                                type="text"
                                size="small"
                                icon={<MoreOutlined />}
                                onClick={(e) => e.stopPropagation()}
                              />
                            </Dropdown>
                          </div>
                        )}
                        
                        <Card.Meta
                          title={
                            <div className="course-title">
                              {course.title}
                              {getStatusTag(course.status)}
                            </div>
                          }
                          description={
                            <div className="course-description">
                              <p>{course.description}</p>
                              {course.subject && (
                                <Tag color="blue">{course.subject.name}</Tag>
                              )}
                            </div>
                          }
                        />
                        
                
                      </Card>
                    </List.Item>
                  );
                }}
              />
            )}
          </Spin>
        </Content>
      </Layout>
      
      {/* 创建课程组件 */}
      <CreateCourseComponent
        visible={createCourseVisible}
        onCancel={handleCreateCourseCancel}
        onSuccess={handleCreateCourseSuccess}
        gradeId={selectedGradeId || undefined}
      />
      
      {/* 编辑课程组件 */}
      <CreateCourseComponent
        visible={editCourseVisible}
        onCancel={handleEditCourseCancel}
        onSuccess={handleEditCourseSuccess}
        editingCourse={editingCourse}
        isEdit={true}
      />
    </div>
  );
};

export default CoursePage;