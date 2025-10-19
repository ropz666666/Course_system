export interface MenuItem {
    key: string;
    icon: React.ReactNode;
    label: string;
    path: string;
    children?: SubMenuItem[];
    menuType?: 'workspace' | 'discover';
}

export interface SubMenuItem {
    key: string;
    icon: React.ReactNode;
    label: string;
    path: string;
}