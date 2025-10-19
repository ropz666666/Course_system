import React, { useState, useRef, FC } from 'react';
import { Input, Button, Tooltip, Image, message } from 'antd';
import { SendOutlined, UploadOutlined, CloseOutlined } from "@ant-design/icons";
import './index.css';
import { uploadFile } from "../../../api/upload";
import { MessageContent } from "../../../types/conversationType.ts";
import {getFileIcon} from "../../../utils/MessageFileRender.ts";

interface FileMessageContent extends MessageContent {
    fileName?: string;
    fileType: 'image' | 'file'; // Only these two types
}

interface MessageInputComponentProps {
    sendMessage: (content: MessageContent[]) => void;
    generating: boolean;
    abortControllerRef: React.RefObject<AbortController | null>;
}

const MessageInputComponent: FC<MessageInputComponentProps> = ({
                                                                   sendMessage,
                                                                   generating,
                                                                   abortControllerRef,
                                                               }) => {
    const [content, setContent] = useState<FileMessageContent[]>([]);
    const [inputText, setInputText] = useState<string>("");
    const fileInputRef = useRef<HTMLInputElement | null>(null);

    // Supported file types
    const supportedFileTypes = [
        'image/*', // All image types
        '.txt',    // Text files
        '.doc',    // Word documents
        '.docx',
        '.md',     // Markdown
        '.xlsx',   // Excel
        '.pdf',    // PDF files
        '.mp3'
    ];

    const uploadFileMessage = () => {
        if (!fileInputRef.current) {
            fileInputRef.current = document.createElement('input');
            fileInputRef.current.type = 'file';
            fileInputRef.current.accept = supportedFileTypes.join(',');
            fileInputRef.current.multiple = false;
            fileInputRef.current.onchange = handleFileChange;
        }
        fileInputRef.current.click();
    };

    const handleFileChange = async (e: Event) => {
        const target = e.target as HTMLInputElement;
        const file = target.files?.[0];
        if (!file) return;

        // Check file extension
        const fileExtension = file.name.split('.').pop()?.toLowerCase() || '';
        const isSupported = supportedFileTypes.some(type => {
            return type.endsWith('/*') ? file.type.startsWith(type.split('/*')[0])
                : type.startsWith('.') ? `.${fileExtension}` === type
                    : file.type === type;
        });

        if (!isSupported) {
            message.error(`Unsupported file type. Please upload: ${supportedFileTypes.join(', ')}`);
            return;
        }

        try {
            const uploadedFileUrl = await uploadFile(file);
            const fileType = file.type.startsWith('image/') ? 'image' : 'file';

            setContent(prev => [
                ...prev,
                {
                    type: fileType, // Base type from MessageContent
                    fileType,     // Our custom type
                    content: `${import.meta.env.VITE_API_BASE_URL}${uploadedFileUrl.url}`,
                    fileName: file.name
                }
            ]);
        } catch (error) {
            message.error("File upload failed");
            console.error("Upload error:", error);
        } finally {
            if (fileInputRef.current) {
                fileInputRef.current.value = '';
            }
        }
    };

    const deleteFileMessage = (index: number) => {
        setContent(prev => prev.filter((_, idx) => idx !== index));
    };



    const renderFileContent = (content: FileMessageContent, index: number) => {
        if (content.fileType === 'image') {
            return (
                <div className="input-image-container" key={index}>
                    <Image
                        style={{ borderRadius: '10px' }}
                        width={80}
                        src={content.content}
                        alt="Uploaded content"
                    />
                    <CloseOutlined
                        className="delete-icon"
                        onClick={() => deleteFileMessage(index)}
                    />
                </div>
            );
        }

        // For non-image files
        const displayName = content.fileName || content.content.split('/').pop() || 'file';
        return (
            <div className="input-file-container" key={index}>
                <div style={{ display: 'flex', alignItems: 'center' }}>
                    <span style={{ marginRight: 8, fontSize: '1.2em' }}>
                        {getFileIcon(content.content)}
                    </span>
                    <div
                        className="file-name"
                        title={displayName}
                    >
                        <a
                            href={content.content}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="file-link"
                        >
                            {displayName}
                        </a>
                    </div>
                </div>
                <CloseOutlined
                    className="delete-icon"
                    onClick={() => deleteFileMessage(index)}
                />
            </div>
        );
    };

    const handleSendMessage = () => {
        if (!inputText.trim() && content.length === 0) {
            message.info("Please enter your query");
            return;
        }

        const messageContent: MessageContent[] = [
            ...content,
            { type: "text", content: inputText }
        ];

        sendMessage(messageContent);
        setInputText("");
        setContent([]);
    };

    const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            handleSendMessage();
        }
    };

    const handleResponseStop = () => {
        abortControllerRef.current?.abort("User manually stopped the request");
    };

    return (
        <div className="message-input-container">
            {/* File preview area */}
            {content.length > 0 && (
                <div className="file-preview-container">
                    {content.map((fileContent, index) => (
                        renderFileContent(fileContent, index)
                    ))}
                </div>
            )}

            {/* Text input area */}
            <Input.TextArea
                placeholder="Type your question here, press Enter to send"
                value={inputText}
                variant="borderless"
                autoSize={{ maxRows: 10, minRows: 2 }}
                onChange={(e) => setInputText(e.target.value)}
                onKeyDown={handleKeyDown}
                disabled={generating}
            />

            {/* Action buttons */}
            <div className="action-buttons">
                <Tooltip title="Upload File">
                    <Button
                        onClick={uploadFileMessage}
                        disabled={generating}
                        icon={<UploadOutlined />}
                    />
                </Tooltip>

                {generating ? (
                    <Tooltip title="Stop generating">
                        <Button
                            danger
                            onClick={handleResponseStop}
                            icon={<CloseOutlined />}
                        />
                    </Tooltip>
                ) : (
                    <Tooltip title="Send message">
                        <Button
                            type="primary"
                            onClick={handleSendMessage}
                            disabled={!inputText.trim() && content.length === 0}
                            icon={<SendOutlined />}
                        />
                    </Tooltip>
                )}
            </div>
        </div>
    );
};

export default MessageInputComponent;