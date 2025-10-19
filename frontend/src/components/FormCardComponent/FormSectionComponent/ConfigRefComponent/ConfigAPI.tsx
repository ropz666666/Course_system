import { useState} from 'react';
import {Button, Input, List, message, Space, Card, Alert} from 'antd';
import {useEffect} from "react";
import {useDispatchGlobalState, useGlobalStateSelector} from "../../../../hooks/global.js";
import {useAgentSelector, useDispatchAgent} from "../../../../hooks/agent.js";
import {parseRefString} from "../../../../utils/parseRefString.ts";

interface APIParams {
  [key: string]: string; // 允许任意字符串键，值为string类型
}

const ConfigAPIComponent = () => {
  const { selectedVariable } = useGlobalStateSelector((state) => state.global);
  const dispatch = useDispatchAgent();
  const agentDetail = useAgentSelector((state) => state.agent.agentDetail);

  const { changeIsVariableShow } = useDispatchGlobalState();

  const [uuid, setUuid] = useState('');
  const [APIParam, setAPIParam] = useState<APIParams>({});
  const [APIOutput, setAPIOutput] = useState('');
  const selectedAPI = agentDetail?.plugins.find((api) => api.uuid === uuid) ;

  useEffect(() => {
    const { uuid, query, outputVariable } = parseRefString(selectedVariable.data);
    setUuid(uuid);
    setAPIOutput(outputVariable);
    if (selectedAPI) {
      let api_param = JSON.stringify(selectedAPI.api_parameter)
          .replace(/\${/g, '')
          .replace(/\}\$/g, '');
      api_param = JSON.parse(api_param);
      const new_param = Object.fromEntries(
          Object.entries(api_param).map(([key, value]) => [
            key,
            Object.prototype.hasOwnProperty.call(query, key) ? query[key] : value,
          ])
      );
      setAPIParam(new_param);
    }
  }, [selectedVariable, selectedAPI]);

  const handleParameterInput = (key: string, fieldType: string, value: string) => {
    const newParameter = { ...APIParam };
    if (fieldType === 'key') return;
    newParameter[key] = value;
    setAPIParam(newParameter);
  };

  const handleOk = async () => {
    if (agentDetail && selectedAPI) {
      const input_param = Object.fromEntries(
          Object.entries(APIParam).map(([key, value]) => [key, `\${${value}}$`])
      );
      const state = `~refAPI{${selectedAPI.uuid}}[${JSON.stringify(input_param)}][\${${APIOutput}}$]/refAPI`;
      const spl_text = JSON.stringify(agentDetail.spl_form);
      const search_text = JSON.stringify(selectedVariable.data).slice(1, -1);
      const replace_text = JSON.stringify(state).slice(1, -1);
      // 辅助函数：转义正则表达式中的特殊字符
      function escapeRegExp(string: string) {
        return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
      }
      // 使用正则表达式进行全局替换
      const regex = new RegExp(escapeRegExp(search_text), 'g');
      const new_spl = spl_text.replace(regex, replace_text);

      dispatch.setAgentPartialInfo({ spl_form: [...JSON.parse(new_spl)] });
      message.success("参数设置成功！");
      changeIsVariableShow();
    }
  };

  return (
      <div style={{
        padding: "16px",
        height: '100%',
        overflowY: "auto",
        background: '#f8f9fa',
        borderRadius: '8px'
      }}>
        {/* 标题区域 */}
        <Alert
            message="参见设置提示"
            description="请仔细填写以下参数信息，确保能够正确访问插件"
            type="info"
            showIcon
            style={{ marginBottom: '16px' }}
        />

        {/* 参数列表区域 */}
        {(Object.keys(APIParam).length > 0) && (
            <Card
                size="small"
                title={<span style={{ fontSize: '14px' }}>插件参数配置</span>}
                style={{ marginBottom: '16px' }}
            >
              <List
                  size="small"
                  dataSource={Object.entries(APIParam)}
                  renderItem={([key, value]) => (
                      <List.Item style={{
                        padding: '12px 16px',
                        borderBottom: '1px solid #f0f0f0',
                      }}>
                        <Space style={{ width: '100%' }} align="center">
                          <Input
                              addonBefore={
                                <span style={{
                                  width: '80px',
                                  display: 'inline-block',
                                  textAlign: 'center'
                                }}>参数名</span>
                              }
                              value={key}
                              disabled
                              style={{ flex: 1 }}
                          />
                          <Input
                              addonBefore={
                                <span style={{
                                  width: '80px',
                                  display: 'inline-block',
                                  textAlign: 'center'
                                }}>参数值</span>
                              }
                              value={value}
                              onChange={(e) => handleParameterInput(key, "value", e.target.value)}
                              style={{ flex: 2 }}
                          />
                        </Space>
                      </List.Item>
                  )}
              />
            </Card>
        )}

        {/* API输出名称区域 */}
        <Card
            size="small"
            title={<span style={{ fontSize: '14px' }}>API输出设置</span>}
            style={{ marginBottom: '16px' }}
        >
          <Input
              placeholder="请输入输出名称，例如: output_data"
              value={APIOutput}
              onChange={(e) => setAPIOutput(e.target.value)}
              allowClear
          />
        </Card>

        {/* 确认按钮 */}
        <Button
            type="primary"
            size="middle"
            block
            style={{
              marginTop: '16px',
              height: '40px',
              fontWeight: '500'
            }}
            onClick={handleOk}
        >
          确认设置
        </Button>
      </div>
  );
};

export default ConfigAPIComponent;
