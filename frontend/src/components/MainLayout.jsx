import React, { useState } from "react";
import { Layout, Menu, Button, Dropdown, Avatar, Typography } from "antd";
import {
  UserOutlined, LogoutOutlined, AppstoreOutlined,
  CalendarOutlined, MedicineBoxOutlined, RobotOutlined,
  FileTextOutlined, TeamOutlined, SettingOutlined
} from "@ant-design/icons";
import { useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import ProfileModal from "./ProfileModal";

const { Header, Sider, Content } = Layout;
const { Text } = Typography;

export default function MainLayout({ children }) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [profileOpen, setProfileOpen] = useState(false);

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  const adminMenuItems = [
    { key: "/admin", icon: <AppstoreOutlined />, label: "仪表盘" },
    { key: "/admin/users", icon: <TeamOutlined />, label: "用户管理" },
    { key: "/admin/doctors", icon: <MedicineBoxOutlined />, label: "医师审核" },
    { key: "/admin/settings", icon: <SettingOutlined />, label: "系统设置" },
  ];

  const doctorMenuItems = [
    { key: "/doctor", icon: <AppstoreOutlined />, label: "工作台" },
    { key: "/doctor/appointments", icon: <CalendarOutlined />, label: "预约管理" },
    { key: "/doctor/records", icon: <FileTextOutlined />, label: "诊疗记录" },
  ];

  const patientMenuItems = [
    { key: "/patient/appointments", icon: <CalendarOutlined />, label: "预约挂号" },
    { key: "/patient/my-appointments", icon: <FileTextOutlined />, label: "我的挂号" },
    { key: "/patient/ai", icon: <RobotOutlined />, label: "AI问诊" },
    { key: "/patient/records", icon: <FileTextOutlined />, label: "就诊记录" },
  ];

  const menuItems = user?.role === "admin" ? adminMenuItems
    : user?.role === "doctor" ? doctorMenuItems
    : patientMenuItems;

  const currentPath = "/" + location.pathname.split("/").slice(1, 3).join("/");

  const userMenu = {
    items: [
      { key: "profile", icon: <UserOutlined />, label: "个人信息" },
      { type: "divider" },
      { key: "logout", icon: <LogoutOutlined />, label: "退出登录", danger: true },
    ],
    onClick: ({ key }) => {
      if (key === "profile") setProfileOpen(true);
      if (key === "logout") handleLogout();
    },
  };

  return (
    <Layout style={{ minHeight: "100vh" }}>
      <Sider breakpoint="lg" collapsedWidth="0" theme="dark">
        <div style={{ height: 64, display: "flex", alignItems: "center", justifyContent: "center", color: "#fff", fontSize: 16, fontWeight: "bold" }}>
          🏥 AI医疗系统
        </div>
        <Menu theme="dark" mode="inline"
          selectedKeys={[currentPath]}
          items={menuItems}
          onClick={({ key }) => navigate(key)}
        />
      </Sider>
      <Layout>
        <Header style={{ background: "#fff", padding: "0 24px", display: "flex", justifyContent: "flex-end", alignItems: "center", borderBottom: "1px solid #f0f0f0" }}>
          <Dropdown menu={userMenu}>
            <div style={{ cursor: "pointer", display: "flex", alignItems: "center", gap: 8 }}>
              <Avatar icon={<UserOutlined />} />
              <Text>{user?.real_name || user?.username}</Text>
            </div>
          </Dropdown>
        </Header>
        <Content style={{ margin: 24, minHeight: 280 }}>
          {children}
        </Content>
      </Layout>
      <ProfileModal open={profileOpen} onClose={() => setProfileOpen(false)} />
    </Layout>
  );
}
