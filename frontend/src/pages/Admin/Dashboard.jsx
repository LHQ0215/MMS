import React, { useState, useEffect } from "react";
import { Card, Row, Col, Table, Statistic, Spin, Alert } from "antd";
import { TeamOutlined, UserOutlined, MedicineBoxOutlined, CalendarOutlined } from "@ant-design/icons";
import { userAPI, doctorAPI, appointmentAPI, adminAPI } from "../../api";

export default function AdminDashboard() {
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({ users: 0, doctors: 0, patients: 0, appointments: 0 });
  const [recentUsers, setRecentUsers] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setError(null);
      const [userRes, doctorRes] = await Promise.all([
        userAPI.list({ page: 1, size: 5 }),
        doctorAPI.list({ page: 1, size: 100 }).catch(() => ({ data: { total: 0, items: [] } })),
      ]);
      const users = userRes.data;
      setStats({
        users: users.total || 0,
        doctors: doctorRes.data.total || 0,
        patients: 0,
        appointments: 0,
      });
      setRecentUsers((users.items || []).slice(0, 5));
    } catch (err) {
      setError("无法加载数据，请确保后端服务已启动");
    } finally {
      setLoading(false);
    }
  };

  const columns = [
    { title: "用户名", dataIndex: "username", key: "username" },
    { title: "姓名", dataIndex: "real_name", key: "real_name" },
    { title: "角色", dataIndex: "role", key: "role", render: (r) => ({ admin: "管理员", doctor: "医生", patient: "患者" })[r] || r },
    { title: "状态", dataIndex: "is_active", key: "is_active", render: (v) => v ? "正常" : "已禁用" },
  ];

  if (loading) return <Spin size="large" style={{ display: "block", textAlign: "center", marginTop: 100 }} />;

  return (
    <div>
      {error && <Alert message={error} type="warning" showIcon style={{ marginBottom: 16 }} />}
      <div className="page-header"><h3>管理仪表盘</h3></div>
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={12} sm={6}><Card className="stat-card"><Statistic title="用户总数" value={stats.users} prefix={<TeamOutlined />} valueStyle={{ color: "#1677ff" }} /></Card></Col>
        <Col xs={12} sm={6}><Card className="stat-card"><Statistic title="医生数" value={stats.doctors} prefix={<MedicineBoxOutlined />} valueStyle={{ color: "#52c41a" }} /></Card></Col>
        <Col xs={12} sm={6}><Card className="stat-card"><Statistic title="患者数" value={stats.patients} prefix={<UserOutlined />} valueStyle={{ color: "#faad14" }} /></Card></Col>
        <Col xs={12} sm={6}><Card className="stat-card"><Statistic title="预约数" value={stats.appointments} prefix={<CalendarOutlined />} valueStyle={{ color: "#ff4d4f" }} /></Card></Col>
      </Row>
      <Card title="最近注册用户">
        <Table dataSource={recentUsers} columns={columns} rowKey="id" pagination={false} size="small" />
      </Card>
    </div>
  );
}

