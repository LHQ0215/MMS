import React, { useState } from "react";
import { Form, Input, Button, message, Tabs } from "antd";
import { UserOutlined, LockOutlined } from "@ant-design/icons";
import { useNavigate, Link } from "react-router-dom";
import { authAPI } from "../../api";
import { useAuth } from "../../context/AuthContext";

export default function Login() {
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const { login } = useAuth();

  const onFinish = async (values) => {
    setLoading(true);
    try {
      const res = await authAPI.login(values);
      const data = res.data;
      login(data.access_token, {
        id: data.user_id, username: data.username,
        role: data.role.toLowerCase(), real_name: data.real_name,
      });
      message.success("登录成功");
      const userRole = data.role?.toLowerCase() || ""; switch (userRole) {
        case "admin": navigate("/admin"); break;
        case "doctor": navigate("/doctor"); break;
        default: navigate("/patient/appointments");
      }
    } catch (err) {
      // Error already handled by interceptor
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <h2>?? AI医疗管理系统</h2>
        <p className="subtitle">请登录您的账户</p>
        <Form onFinish={onFinish} layout="vertical" size="large">
          <Form.Item name="username" rules={[{ required: true, message: "请输入用户名" }]}>
            <Input prefix={<UserOutlined />} placeholder="用户名" />
          </Form.Item>
          <Form.Item name="password" rules={[{ required: true, message: "请输入密码" }]}>
            <Input.Password prefix={<LockOutlined />} placeholder="密码" />
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit" loading={loading} block>
              登录
            </Button>
          </Form.Item>
        </Form>
        <div style={{ textAlign: "center" }}>
          还没有账户？<Link to="/register">立即注册</Link>
        </div>
      </div>
    </div>
  );
}
// Login page v1.0 - AI Medical Management System




