import {MenuItem} from '../../../types/menu.ts';
import {
    ShopOutlined,
    ThunderboltOutlined,
    DatabaseOutlined
} from "@ant-design/icons";
import {Menu} from "antd";
import {useNavigate} from "react-router-dom";
import { useState, useEffect } from 'react';

interface DiscoverSubMenuProps {
    items: MenuItem[]
    selectedKeys: string[];
    onItemClick: (key: string) => void;
}

const DiscoverSubMenu = ({items, selectedKeys, onItemClick }: DiscoverSubMenuProps) => {
    const navigate = useNavigate();
    const [expandedKeys, setExpandedKeys] = useState<string[]>([]);
    const [currentSubItems, setCurrentSubItems] = useState<MenuItem[]>([]);

    // 处理二级菜单点击
    const handleSecondLevelClick = (item: MenuItem) => {
        if (item.customChildren && item.customChildren.length > 0) {
            setCurrentSubItems(item.customChildren);
            if (expandedKeys.includes(item.key)) {
                setExpandedKeys(expandedKeys.filter(key => key !== item.key));
                setCurrentSubItems([]);
            } else {
                setExpandedKeys([...expandedKeys.filter(key => key !== item.key), item.key]);
            }
        } else if (item.path) {
            navigate(item.path);
            onItemClick(item.key);
        }
    };

    // 处理三级菜单点击
    const handleThirdLevelClick = (item: MenuItem) => {
        if (item.path) {
            navigate(item.path);
            onItemClick(item.key);
        }
    };

    return (
        <div className="w-[240px] bg-[#FAFAFA] border-l border-[#F2F4F7] py-3 overflow-y-auto max-h-screen">
            <div
                className="mx-3 px-3 py-2 text-[#344054] font-medium text-base flex items-center gap-2 cursor-pointer hover:bg-[#EAECF0] rounded-lg transition-colors duration-200"
                onClick={() => navigate(`/discover`)}
            >
                <div className="w-6 h-6 rounded-md bg-[#7F56D9] flex items-center justify-center text-white">
                    <ShopOutlined className="text-sm" />
                </div>
                <span>实验中心</span>
            </div>

            <div className="mt-3 mx-3 space-y-2">
                {/* 一级菜单 - Sapper 和 UniGraph */}
                {items.map((item) => (
                    <div key={item.key} className="mb-3">
                        <div
                            className={`px-3 py-2.5 text-base flex items-center gap-3 cursor-pointer rounded-lg transition-colors duration-200 ${
                                selectedKeys.includes(item.key) 
                                    ? 'bg-[#7F56D9] text-white' 
                                    : 'text-[#344054] hover:bg-[#EAECF0]'
                            }`}
                            onClick={() => handleSecondLevelClick(item)}
                        >
                            <div className={`w-5 h-5 flex items-center justify-center ${
                                selectedKeys.includes(item.key) ? 'text-white' : 'text-[#7F56D9]'
                            }`}>
                                {item.key === 'sapper' ? <ThunderboltOutlined className="text-sm" /> : <DatabaseOutlined className="text-sm" />}
                            </div>
                            <span className="font-medium">{item.label}</span>
                        </div>

                        {/* 二级菜单 */}
                        {expandedKeys.includes(item.key) && item.customChildren && (
                            <div className="ml-6 mt-2 space-y-1">
                                {item.customChildren.map((subItem) => (
                                    <div key={subItem.key}>
                                        <div
                                            className={`px-3 py-2 text-sm flex items-center gap-2 cursor-pointer rounded-md transition-colors duration-200 ${
                                                selectedKeys.includes(subItem.key)
                                                    ? 'bg-[#E9D5FF] text-[#7F56D9]'
                                                    : 'text-[#6B7280] hover:bg-[#F3F4F6]'
                                            }`}
                                            onClick={() => handleSecondLevelClick(subItem)}
                                        >
                                            <div className="w-4 h-4 flex items-center justify-center">
                                                {subItem.icon}
                                            </div>
                                            <span className="font-medium">{subItem.label}</span>
                                        </div>

                                        {/* 三级菜单 */}
                                        {expandedKeys.includes(subItem.key) && subItem.customChildren && (
                                            <div className="ml-6 mt-1 space-y-1">
                                                {subItem.customChildren.map((thirdItem) => (
                                                    <div
                                                        key={thirdItem.key}
                                                        className={`px-3 py-1.5 text-sm flex items-center gap-2 cursor-pointer rounded-md transition-colors duration-200 ${
                                                            selectedKeys.includes(thirdItem.key)
                                                                ? 'bg-[#E9D5FF] text-[#7F56D9]'
                                                                : 'text-[#9CA3AF] hover:bg-[#F9FAFB]'
                                                        }`}
                                                        onClick={() => handleThirdLevelClick(thirdItem)}
                                                    >
                                                        <div className="w-4 h-4 flex items-center justify-center">
                                                            {thirdItem.icon}
                                                        </div>
                                                        <span>{thirdItem.label}</span>
                                                    </div>
                                                ))}
                                            </div>
                                        )}
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                ))}
            </div>
        </div>
    );
};

export default DiscoverSubMenu;