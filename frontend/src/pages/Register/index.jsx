import React, { useState } from "react";
import { Form, Input, Button, message, Select } from "antd";
import { UserOutlined, LockOutlined } from "@ant-design/icons";
import { useNavigate, Link } from "react-router-dom";
import { authAPI } from "../../api";
import { useAuth } from "../../context/AuthContext";

export default function Register() {
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const { login } = useAuth();

  const onFinish = async (values) => {
    setLoading(true);
    try {
      const res = await authAPI.register(values);
      const data = res.data;
      login(data.access_token, {
        id: data.user_id, username: data.username,
        role: data.role.toLowerCase(), real_name: data.real_name,
      });
      message.success("注册成功");
      if ((data.role?.toLowerCase() || "") === "doctor") {
        navigate("/doctor");
      } else {
        navigate("/patient/appointments");
      }
    } catch (err) {
      // Error handled by interceptor
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <h2>创建账户</h2>
        <p className="subtitle">注册AI医疗管理系统</p>
        <Form onFinish={onFinish} layout="vertical" size="large">
          <Form.Item name="username" label="用户名" rules={[{ required: true, message: "请输入用户名" }, { min: 2, message: "至少2个字符" }]}>
            <Input prefix={<UserOutlined />} placeholder="用户名" />
          </Form.Item>
          <Form.Item name="real_name" label="真实姓名" rules={[{ required: true, message: "请输入真实姓名" }]}>
            <Input placeholder="真实姓名" />
          </Form.Item>
          <Form.Item name="role" label="角色" initialValue="patient" rules={[{ required: true }]}>
            <Select options={[{ value: "patient", label: "患者" }, { value: "doctor", label: "医生" }]} />
          </Form.Item>
          <Form.Item name="password" label="密码" rules={[{ required: true, message: "请输入密码" }, { min: 6, message: "至少6个字符" }]}>
            <Input.Password prefix={<LockOutlined />} placeholder="密码" />
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit" loading={loading} block>
              注册
            </Button>
          </Form.Item>
        </Form>
        <div style={{ textAlign: "center" }}>
          已有账户？<Link to="/login">返回登录</Link>
        </div>
      </div>
    </div>
  );
}



