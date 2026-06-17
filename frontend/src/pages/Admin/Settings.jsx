import React, { useState } from "react";
import { Card, Form, Input, Button, message, Divider, Descriptions, Spin, Alert } from "antd";
import { UserOutlined, LockOutlined, SaveOutlined } from "@ant-design/icons";
import { userAPI, authAPI } from "../../api";
import { useAuth } from "../../context/AuthContext";

export default function AdminSettings() {
  const { user, updateUser } = useAuth();
  const [profileForm] = Form.useForm();
  const [pwdForm] = Form.useForm();
  const [profileLoading, setProfileLoading] = useState(false);
  const [pwdLoading, setPwdLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  const updateProfile = async (values) => {
    setProfileLoading(true);
    setError(null);
    setSuccess(null);
    try {
      await userAPI.updateMe(values);
      updateUser(values);
      setSuccess("个人信息更新成功");
      message.success("更新成功");
    } catch (err) {
      setError("更新失败：" + (err.response?.data?.detail || err.message));
    }
    setProfileLoading(false);
  };

  const changePassword = async (values) => {
    setPwdLoading(true);
    setError(null);
    setSuccess(null);
    try {
      await authAPI.changePassword(values);
      setSuccess("密码修改成功");
      pwdForm.resetFields();
      message.success("密码修改成功");
    } catch (err) {
      setError("密码修改失败：" + (err.response?.data?.detail || err.message));
    }
    setPwdLoading(false);
  };

  if (!user) return <Spin size="large" style={{ display: "block", textAlign: "center", marginTop: 100 }} />;

  return (
    <div>
      <div className="page-header">
        <h3><UserOutlined /> 系统设置</h3>
      </div>

      {error && <Alert message={error} type="error" showIcon closable style={{ marginBottom: 16 }}
        onClose={() => setError(null)} />}
      {success && <Alert message={success} type="success" showIcon closable style={{ marginBottom: 16 }}
        onClose={() => setSuccess(null)} />}

      <Card title="个人信息" style={{ marginBottom: 24 }}>
        <Descriptions column={2} bordered size="small" style={{ marginBottom: 24 }}>
          <Descriptions.Item label="用户名">{user.username}</Descriptions.Item>
          <Descriptions.Item label="角色">{user.role === "admin" ? "管理员" : user.role === "doctor" ? "医生" : "患者"}</Descriptions.Item>
          <Descriptions.Item label="姓名">{user.real_name}</Descriptions.Item>
          <Descriptions.Item label="状态">正常</Descriptions.Item>
        </Descriptions>
        <Divider>修改信息</Divider>
        <Form form={profileForm} layout="vertical" onFinish={updateProfile}
          initialValues={{ real_name: user.real_name, phone: user.phone || "", email: user.email || "" }}>
          <Form.Item name="real_name" label="真实姓名" rules={[{ required: true, message: "请输入姓名" }]}>
            <Input prefix={<UserOutlined />} />
          </Form.Item>
          <Form.Item name="phone" label="手机号码">
            <Input placeholder="请输入手机号码" />
          </Form.Item>
          <Form.Item name="email" label="电子邮箱">
            <Input placeholder="请输入邮箱地址" />
          </Form.Item>
          <Button type="primary" htmlType="submit" loading={profileLoading} icon={<SaveOutlined />}>
            保存修改
          </Button>
        </Form>
      </Card>

      <Card title="修改密码">
        <Form form={pwdForm} layout="vertical" onFinish={changePassword}>
          <Form.Item name="old_password" label="原密码" rules={[{ required: true, message: "请输入原密码" }]}>
            <Input.Password prefix={<LockOutlined />} />
          </Form.Item>
          <Form.Item name="new_password" label="新密码" rules={[
            { required: true, message: "请输入新密码" },
            { min: 6, message: "密码至少6位" },
          ]}>
            <Input.Password prefix={<LockOutlined />} />
          </Form.Item>
          <Button type="primary" htmlType="submit" loading={pwdLoading} icon={<SaveOutlined />}>
            修改密码
          </Button>
        </Form>
      </Card>
    </div>
  );
}
