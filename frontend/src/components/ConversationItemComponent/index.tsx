import { Button, Dropdown, Menu, Popconfirm, Typography, Input } from 'antd';
import { DeleteOutlined, EditFilled, MoreOutlined } from '@ant-design/icons';
import { ConversationRes } from '../../types/conversationType';
import { MenuInfo } from 'rc-menu/lib/interface';
import { useState } from 'react';

const { Text } = Typography;

interface ConversationItemProps {
    conversation: ConversationRes;
    isActive: boolean;
    onClick: () => void;
    onDelete: () => void;
    onRename: (name: string) => void;
}

// 定义样式常量
const STYLE_CONSTANTS = {
    cozePrimary: 'bg-[#6E38F7] hover:bg-[#5D2ED6] border-[#6E38F7] text-white',
    cozeSecondary: 'bg-[#F0EBFF] text-[#6E38F7] border-[#F0EBFF]',
    cozeDark: 'text-[#1A1A1A]',
    cozeBorder: 'border-[#EAE5FF]',
    activeBg: 'bg-[#F0EBFF] p-3',
    hoverBg: 'hover:bg-[#F9F7FF]',
    activeText: 'text-[#6E38F7]',
    hoverText: 'group-hover:text-[#6E38F7]'
};

const ConversationItemComponent = (props: ConversationItemProps) => {
    const {
        conversation,
        isActive,
        onClick,
        onDelete,
        onRename
    } = props;

    const [isEditing, setIsEditing] = useState(false);
    const [editedName, setEditedName] = useState(conversation.name);


    /**
     * 渲染操作菜单内容
     */
    const renderActionMenu = () => (
        <Menu className={`rounded-lg ${STYLE_CONSTANTS.cozeBorder}`}>
            <Menu.Item
                key="edit"
                onClick={(e: MenuInfo) => {
                    e.domEvent.stopPropagation();
                    handleStartEdit();
                }}
                className="hover:bg-[#F0EBFF]"
            >
                <EditFilled />
            </Menu.Item>
            <Menu.Item
                key="delete"
                danger
                className="hover:bg-red-50"
            >
                <div onClick={(e) => e.stopPropagation()}>
                    <Popconfirm
                        title="确定要删除此会话吗？"
                        onConfirm={(e) => {
                            e?.stopPropagation();
                            handleDeleteConfirm();
                        }}
                        onCancel={(e?: React.MouseEvent) => e?.stopPropagation()}
                        okText="确定"
                        cancelText="取消"
                    >
                        <DeleteOutlined />
                    </Popconfirm>
                </div>
            </Menu.Item>
        </Menu>
    );

    /**
     * 开始编辑
     */
    const handleStartEdit = () => {
        setIsEditing(true);
        setEditedName(conversation.name);
    };

    /**
     * 结束编辑
     */
    const handleEndEdit = () => {
        setIsEditing(false);
    };

    /**
     * 提交重命名
     */
    const handleRenameSubmit = () => {
        if (editedName.trim() && editedName !== conversation.name) {
            onRename(editedName.trim());
        }
        handleEndEdit();
    };

    /**
     * 处理删除确认
     */
    const handleDeleteConfirm = (e?: React.MouseEvent) => {
        e?.stopPropagation();
        onDelete();
    };

    /**
     * 渲染编辑状态下的内容
     */
    const renderEditContent = () => (
        <Input
            autoFocus
            value={editedName}
            onChange={(e) => setEditedName(e.target.value)}
            onBlur={handleRenameSubmit}
            onPressEnter={handleRenameSubmit}
            onClick={(e) => e.stopPropagation()}
            className="w-full"
            maxLength={50}
        />
    );

    /**
     * 渲染正常状态下的内容
     */
    const renderNormalContent = () => (
        <Text
            ellipsis={{ tooltip: conversation.name }}
            className={`transition-colors ${
                isActive
                    ? STYLE_CONSTANTS.activeText
                    : `${STYLE_CONSTANTS.cozeDark} ${STYLE_CONSTANTS.hoverText}`
            }`}
        >
            {conversation.name}
        </Text>
    );

    return (
        <div
            className={`px-3 py-1 cursor-pointer group transition-colors m-2 rounded-lg flex ${
                isActive ? STYLE_CONSTANTS.activeBg : STYLE_CONSTANTS.hoverBg
            }`}
            onClick={onClick}
        >
            <div className={`w-[180px] justify-start flex`}>
                {isEditing ? renderEditContent() : renderNormalContent()}
            </div>
            <Dropdown
                overlay={renderActionMenu()}
                trigger={['click']}
                placement="bottomRight"
                getPopupContainer={(triggerNode) => triggerNode.parentElement as HTMLElement}
            >
                <Button
                    type="text"
                    icon={<MoreOutlined className="text-[#999999] hover:text-[#6E38F7]" />}
                    onClick={(e) => e.stopPropagation()}
                    className="hover:bg-[#F0EBFF] w-[30px] h-[30px] items-center"
                    aria-label="更多操作"
                />
            </Dropdown>
        </div>
    );
};

export default ConversationItemComponent;