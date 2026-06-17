import React, { useState, useEffect } from "react";
import { Card, Row, Col, Statistic, Modal, Form, Input, DatePicker, Select, message, Alert, Spin, Button } from "antd";
import { MedicineBoxOutlined, UserOutlined, CalendarOutlined, AppstoreOutlined } from "@ant-design/icons";
import { appointmentAPI, doctorAPI, departmentAPI } from "../../api";
import dayjs from "dayjs";

export default function DoctorWorkbench() {
  const [doctor, setDoctor] = useState(null);
  const [appointments, setAppointments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showProfileSetup, setShowProfileSetup] = useState(false);
  const [departments, setDepartments] = useState([]);
  const [profileForm] = Form.useForm();

  useEffect(() => { loadData(); }, []);

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [docRes, apptRes] = await Promise.all([
        doctorAPI.getProfile().catch(() => null),
        appointmentAPI.getDoctor({ page: 1, size: 200 }).catch(() => ({ data: { items: [] } })),
      ]);
      if (docRes) {
        setDoctor(docRes.data);
      } else {
        const deptRes = await departmentAPI.list();
        setDepartments(deptRes.data.items || []);
        setShowProfileSetup(true);
      }
      setAppointments(apptRes.data.items || []);
    } catch (err) {
      setError("加载失败，请确保已完成医生注册并通过审核");
    }
    setLoading(false);
  };

  const submitProfileSetup = async (values) => {
    try {
      await doctorAPI.register(values);
      message.success("医师资料已提交，可以开始工作了");
      setShowProfileSetup(false);
      loadData();
    } catch (err) { }
  };

  const todayCount = appointments.filter(a => a.appointment_date === dayjs().format("YYYY-MM-DD")).length;
  const pendingCount = appointments.filter(a => a.status === "pending" || a.status === "confirmed").length;
  const completedCount = appointments.filter(a => a.status === "completed").length;

  const statusCounts = {
    pending: appointments.filter(a => a.status === "pending").length,
    confirmed: appointments.filter(a => a.status === "confirmed").length,
  };

  if (loading) return <Spin size="large" style={{ display: "block", textAlign: "center", marginTop: 100 }} />;

  return (
    <div>
      {error && <Alert message={error} type="warning" showIcon style={{ marginBottom: 16 }} />}
      <div className="page-header">
        <h3><AppstoreOutlined /> 医生工作台</h3>
        <p style={{ color: "#666", margin: 0 }}>欢迎回来，{doctor?.real_name || "医生"}</p>
      </div>

      {doctor && (
        <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
          <Col xs={12} sm={6}><Card className="stat-card">
            <Statistic title="所属科室" value={doctor.department_name || "未设置"} prefix={<MedicineBoxOutlined />} />
          </Card></Col>
          <Col xs={12} sm={6}><Card className="stat-card">
            <Statistic title="职称" value={doctor.title || "未设置"} prefix={<UserOutlined />} />
          </Card></Col>
          <Col xs={12} sm={6}><Card className="stat-card">
            <Statistic title="今日预约" value={todayCount} prefix={<CalendarOutlined />} valueStyle={{ color: "#1677ff" }} />
          </Card></Col>
          <Col xs={12} sm={6}><Card className="stat-card">
            <Statistic title="待处理" value={pendingCount} prefix={<CalendarOutlined />} valueStyle={{ color: "#faad14" }} />
          </Card></Col>
        </Row>
      )}

      <Modal title="填写医师资料" open={showProfileSetup} closable={false} maskClosable={false} footer={null} width={640}>
        <Form form={profileForm} layout="vertical" onFinish={submitProfileSetup}>
          <Form.Item name="department_id" label="所属科室" rules={[{ required: true, message: "请选择科室" }]}>
            <Select showSearch placeholder="请选择科室" optionFilterProp="label"
              options={departments.map(d => ({ value: d.id, label: d.name }))} />
          </Form.Item>
          <Form.Item name="title" label="职称" rules={[{ required: true, message: "请输入职称" }]}>
            <Select placeholder="请选择职称"
              options={[{ value: "主任医师", label: "主任医师" }, { value: "副主任医师", label: "副主任医师" }, { value: "主治医师", label: "主治医师" }, { value: "住院医师", label: "住院医师" }, { value: "医士", label: "医士" }]} />
          </Form.Item>
          <Form.Item name="specialization" label="专业特长">
            <Input placeholder="如：心血管疾病、消化系统疾病" />
          </Form.Item>
          <Form.Item name="license_number" label="执业证号" rules={[{ required: true, message: "请输入执业证号" }]}>
            <Input placeholder="请输入执业医师证号" />
          </Form.Item>
          <Form.Item name="consultation_fee" label="挂号费(元)" rules={[{ required: true, message: "请输入挂号费" }]}>
            <Input type="number" placeholder="如：20" />
          </Form.Item>
          <Form.Item name="max_daily_patients" label="每日最大接诊数" initialValue={30}>
            <Input type="number" />
          </Form.Item>
          <Form.Item name="introduction" label="个人简介">
            <Input.TextArea rows={3} placeholder="请简单介绍您的专业背景和擅长领域" />
          </Form.Item>
          <Button type="primary" htmlType="submit" block size="large">
            提交并开始工作
          </Button>
        </Form>
      </Modal>
    </div>
  );
}
