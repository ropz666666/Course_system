import React, { useState, useEffect, useRef } from 'react';
import { List, Button, Tooltip, Spin} from 'antd';
import {DownloadOutlined, RedoOutlined} from "@ant-design/icons";
import {
    ChatMessageItem,
    MessageContent, SystemMessageContent
} from "../../../types/conversationType.ts";
import './index.css';
import {SystemMessageComponent, UserMessageComponent} from "./RenderMessageComponent";
import {mdToDocxAPI} from "../../../api/util.ts";

interface ChatContainerProps {
    welcomeInfo?: string;
    messages: ChatMessageItem[];
    suggestions: [];
    onMessagesChange?: (messages: ChatMessageItem[]) => void;
    sendMessage: (contents: MessageContent[]) => void;
    generating: boolean;
    outputChaining: boolean;
}

const ChatContainerComponent: React.FC<ChatContainerProps> = ({
                                                                  welcomeInfo = '',
                                                                  messages = [],
                                                                  suggestions = [],
                                                                  onMessagesChange,
                                                                  sendMessage,
                                                                  generating,
                                                                  outputChaining
                                                              }) => {
    const [shouldSendMessage, setShouldSendMessage] = useState<boolean>(false);
    const [messageQuery, setMessageQuery] = useState<MessageContent[] | null>(null);
    const chatContainerRef = useRef<HTMLDivElement>(null);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    // Auto-scroll to bottom when messages or generating state changes
    useEffect(() => {
        scrollToBottom();
    }, [messages, generating]);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    const handleSendMessage = (index: number) => {
        if (index > 1) {
            const prevMessage = messages[index - 1];

            // 确保是用户消息且有contents属性
            if (prevMessage?.role === 'user' && 'contents' in prevMessage) {
                const query = [...prevMessage.contents];
                const newMessages = messages.slice(0, index - 1);

                if (onMessagesChange) {
                    onMessagesChange(newMessages);
                }
                setMessageQuery(query);
                setShouldSendMessage(true);
            }
        }
    };

    const handleSuggestionClick = (suggestion: string) => {
        const newMessage: MessageContent[] = [{type: "text", content: suggestion}];
        sendMessage(newMessage);
    }

    useEffect(() => {
        if (shouldSendMessage && messageQuery) {
            sendMessage(messageQuery);
            setShouldSendMessage(false);
        }
    }, [shouldSendMessage, messageQuery, sendMessage]);

    const handleMessageSave = async (message: SystemMessageContent[]) => {
        try {
            // 1. 拼接所有消息内容
            let note = '';
            message.forEach((unit) => {
                unit.output.forEach((item) => {
                    note += item.content;
                });
            });

            // 2. 调用API转换为docx
            const res = await mdToDocxAPI(note);
            if (!res?.url) {
                throw new Error('Failed to generate document: No URL returned');
            }

            // 3. 创建隐藏的下载链接
            const a = document.createElement('a');
            a.href = res.url;
            a.download = `document_${new Date().getTime()}.docx`; // 使用时间戳作为文件名
            a.style.display = 'none';

            // 4. 触发下载
            document.body.appendChild(a);
            a.click();

            // 5. 清理DOM
            setTimeout(() => {
                document.body.removeChild(a);
                // 可选：释放Blob URL（如果是Blob URL）
                if (res.url.startsWith('blob:')) {
                    URL.revokeObjectURL(res.url);
                }
            }, 100);

            return { success: true, url: res.url };
        } catch (error) {
            console.error('Document save failed:', error);
            return {
                success: false,
                error: error instanceof Error ? error.message : 'Unknown error'
            };
        }
    };

    return (
        <div className="chat-container" ref={chatContainerRef}>
            {welcomeInfo && (
                <div className="welcome-message-container">
                    <div className="welcome-message">
                        <div style={{
                            whiteSpace: 'pre-wrap',
                            backgroundColor: '#f0f0f0',
                            padding: '10px',
                            borderRadius: '10px',
                        }}>
                            {welcomeInfo}
                        </div>
                    </div>
                </div>
            )}

            {messages.length > 0 && (
                <List
                    dataSource={messages}
                    renderItem={(item: ChatMessageItem, itemIndex: number) => (
                        <List.Item
                            className={`message-item ${item.role}`}
                            style={{
                                justifyContent: item.role === 'user' ? 'flex-end' : 'flex-start',
                                padding: '8px 0'
                            }}
                        >
                            <div className={`message-bubble ${item.role}`}>
                                {item.role === 'user' && <UserMessageComponent message={item} />}
                                {item.role === 'system' && <SystemMessageComponent message={item} outputChaining={outputChaining} />}
                                {item.role === 'system' && !generating && (
                                    <>
                                        <Tooltip placement="right">
                                            <Button
                                                style={{display: "none"}}
                                                type="text"
                                                icon={<RedoOutlined />}
                                                onClick={() => handleSendMessage(itemIndex)}
                                            />
                                        </Tooltip>
                                        <Tooltip
                                            placement="right"
                                            title="导出为Word文档"
                                            mouseEnterDelay={0.3}
                                        >
                                            <Button
                                                type="text"
                                                icon={<DownloadOutlined style={{ color: '#1890ff' }} />}
                                                onClick={() => handleMessageSave(item.units)}
                                                aria-label="export-document" // 无障碍支持
                                            />
                                        </Tooltip>
                                    </>
                                )}
                                {item.role === 'system' && messages.length - 1 === itemIndex && generating && (
                                    <>
                                        <Spin size="small" style={{ paddingRight: '10px' }} />
                                        <span>思考中...</span>
                                    </>
                                )}
                            </div>
                        </List.Item>
                    )}
                />
            )}
            {/*猜你想问，提问建议*/}
            {suggestions.length > 0 && (
                <List
                    itemLayout={"vertical"}
                    dataSource={suggestions}
                    renderItem={(item: string) => (
                        <div style={{paddingBottom: '10px'}}>
                            <Button onClick={() => handleSuggestionClick(item)}>
                                {item}
                            </Button>
                        </div>
                    )}
                />
            )}
            <div ref={messagesEndRef} />
        </div>
    );
};

export default ChatContainerComponent;