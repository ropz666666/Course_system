import { Button, Divider, Form, Input, Select, Space, Tag, Tooltip } from 'antd';
import { MinusOutlined, PlusOutlined } from "@ant-design/icons";
import { PluginDetail } from "../../types/pluginType.ts";
import {useEffect} from "react";
const { Item } = Form;

const { Option } = Select;

const PluginFormComponent = ({ plugin_data, handleChange }: { plugin_data?: PluginDetail, handleChange: (values: PluginDetail) => void }) => {
    const [form] = Form.useForm();
    // Default form structure
    const initFormData = {
        name: '',
        description: '',
        server_url: "",
        content_type: "",
        authorization: "",
        return_value_type: "",
        parse_path: [],
        api_parameter: []
    };

    // Initialize form
    useEffect(() => {
        const initialValues = {
            ...initFormData,
            ...plugin_data,
            // Convert api_parameter object to array if needed
            api_parameter: plugin_data?.api_parameter
                ? Object.entries(plugin_data?.api_parameter).map(([key, value]) => ({ key, value }))
                : []
        };
        form.setFieldsValue(initialValues);
    }, [plugin_data]);

    const onValuesChange = (_: Partial<PluginDetail>, allValues: PluginDetail) => {
        let api_parameter: Record<string, string> = {};

        // Check if api_parameter is an array and transform it
        if (Array.isArray(allValues.api_parameter)) {
            api_parameter = allValues.api_parameter.reduce((acc: Record<string, string>, item: { key?: string, value?: string }) => {
                if (item?.key) {
                    acc[item.key] = item.value || '';
                }
                return acc;
            }, {});
        } else if (typeof allValues.api_parameter === 'object' && allValues.api_parameter !== null) {
            // If it's already an object, use it directly
            api_parameter = { ...allValues.api_parameter };
        }

        handleChange({
            ...allValues,
            api_parameter
        });
    };

    return (
        <Form
            form={form}
            style={{width: '100%'}}
            layout="vertical"
            onValuesChange={onValuesChange}
            initialValues={plugin_data}
        >
            <Divider orientation="left" orientationMargin="0">
                <Tag bordered={false} color="blue">名称</Tag>
            </Divider>
            <Form.Item name="name">
                <Input />
            </Form.Item>

            <Divider orientation="left" orientationMargin="0">
                <Tag bordered={false} color="blue">描述</Tag>
            </Divider>
            <Form.Item name="description">
                <Input.TextArea autoSize={{ minRows: 2, maxRows: 5 }} />
            </Form.Item>

            <Divider orientation="left" orientationMargin="0">
                <Tag bordered={false} color="blue">服务器URL</Tag>
            </Divider>
            <Form.Item name="server_url">
                <Input.TextArea autoSize={{ minRows: 1, maxRows: 5 }} />
            </Form.Item>

            <Divider orientation="left" orientationMargin="0">
                <Tag bordered={false} color="blue">内容类型</Tag>
            </Divider>
            <Form.Item name="content_type">
                <Select style={{ width: '100%' }} placeholder="Select Content Type">
                    <Option value="application/json">json</Option>
                    <Option value="application/octet-stream">octet-stream</Option>
                </Select>
            </Form.Item>

            <Divider orientation="left" orientationMargin="0">
                <Tag bordered={false} color="blue">认证方式</Tag>
            </Divider>
            <Form.Item name="authorization">
                <Input />
            </Form.Item>

            <Divider orientation="left" orientationMargin="0">
                <Tag bordered={false} color="blue">返回值类型</Tag>
            </Divider>
            <Form.Item name="return_value_type">
                <Select style={{ width: '100%' }} placeholder="Select ReturnValue Type">
                    {['Text', "Url", "Image_Binary_Data", "Speech_Binary_Data", "Image_B64_Data", "Speech_B64_Data"].map((option) => (
                        <Option key={option} value={option}>{option}</Option>
                    ))}
                </Select>
            </Form.Item>

            <Divider orientation="left" orientationMargin="0">
                <Tag bordered={false} color="blue">解析路径</Tag>
            </Divider>
            <Form.List name="parse_path">
                {(fields, { add, remove }) => (
                    <>
                        <div style={{ display: 'flex', gap: 8, marginBottom: 8, overflow: 'auto', paddingBottom: '8px'}}>
                            {fields.map(({ key, name, ...restField }) => (
                                <Space.Compact block key={key} style={{ display: 'flex', alignItems: 'center' }}>
                                    <Item
                                        {...restField}
                                        name={name}
                                        key={key}
                                        style={{ marginBottom: 0 }}
                                    >
                                        <Input
                                            placeholder="Path segment"
                                            style={{ width: 160 }}
                                        />
                                    </Item>
                                    <Tooltip title="Remove path segment">
                                        <Button
                                            icon={<MinusOutlined />}
                                            onClick={() => remove(name)}
                                            danger
                                            style={{ color: '#ff4d4f' }}
                                        />
                                    </Tooltip>
                                </Space.Compact>
                            ))}
                        </div>
                        <Button
                            type="dashed"
                            icon={<PlusOutlined />}
                            onClick={() => add('')}
                            style={{ width: 160 }}
                        >
                            Add path segment
                        </Button>
                    </>
                )}
            </Form.List>

            <Divider orientation="left" orientationMargin="0">
                <Tag bordered={false} color="blue">参数</Tag>
            </Divider>
            <Form.List name="api_parameter">
                {(fields, { add, remove }) => (
                    <>
                        {fields.map(({ key, name, ...restField }) => (
                            <Item key={key} style={{marginBottom: '5px'}}>
                                <Space.Compact style={{ width: '100%'}} size="middle">
                                    <Form.Item
                                        {...restField}
                                        name={[name, 'key']}
                                        noStyle
                                    >
                                        <Input addonBefore="Param" />
                                    </Form.Item>
                                    <Form.Item
                                        {...restField}
                                        name={[name, 'value']}
                                        noStyle
                                    >
                                        <Input addonBefore="Value" />
                                    </Form.Item>
                                    <Tooltip title="Remove item">
                                        <Button
                                            icon={<MinusOutlined />}
                                            onClick={() => remove(name)}
                                        />
                                    </Tooltip>
                                </Space.Compact>
                            </Item>
                        ))}
                        <Tooltip title="Add item">
                            <Button
                                icon={<PlusOutlined />}
                                onClick={() => add({ key: `param_${Date.now()}`, value: '' })}
                            />
                        </Tooltip>
                    </>
                )}
            </Form.List>
        </Form>
    );
};

export default PluginFormComponent;