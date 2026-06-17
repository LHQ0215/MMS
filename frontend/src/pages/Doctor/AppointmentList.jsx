import React, { useState, useEffect } from "react";
import { Card, Table, Tag, Button, Space, Select, DatePicker, message, Spin, Empty, Alert, Row, Col, Statistic, Modal, Input, Form } from "antd";
import { ReloadOutlined, CheckCircleOutlined, CloseCircleOutlined, CalendarOutlined, TeamOutlined, MedicineBoxOutlined } from "@ant-design/icons";
import { appointmentAPI, doctorAPI, diagnosisAPI } from "../../api";
import dayjs from "dayjs";

export default function DoctorAppointmentList() {
  const [doctor, setDoctor] = useState(null);
  const [appointments, setAppointments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [statusFilter, setStatusFilter] = useState(null);
  const [dateFilter, setDateFilter] = useState(null);
  const [stats, setStats] = useState({ total: 0, completed: 0, pending: 0, cancelled: 0 });

  // 诊断弹窗
  const [diagnosisModal, setDiagnosisModal] = useState(false);
  const [currentAppt, setCurrentAppt] = useState(null);
  const [formKey, setFormKey] = useState(0);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => { loadDoctorProfile(); }, []);

  useEffect(() => {
    if (doctor) loadAppointments();
  }, [doctor, statusFilter, dateFilter]);

  const loadDoctorProfile = async () => {
    try {
      const res = await doctorAPI.getProfile();
      setDoctor(res.data);
    } catch (err) {
      setError("请先完成医生注册并通过审核");
    }
  };

  const loadAppointments = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await appointmentAPI.getDoctor({
        page: 1, size: 100,
        status_filter: statusFilter || undefined,
        date_filter: dateFilter || undefined,
      });
      const items = res.data.items || [];
      setAppointments(items);
      setStats({
        total: res.data.total || 0,
        completed: items.filter((a) => a.status === "completed").length,
        pending: items.filter((a) => a.status === "confirmed" || a.status === "pending").length,
        cancelled: items.filter((a) => a.status === "cancelled" || a.status === "missed").length,
      });
    } catch (err) {
      setError("加载预约列表失败");
    }
    setLoading(false);
  };

  // 打开诊断弹窗
  const openDiagnosis = (appt) => {
    setCurrentAppt(appt);
    setFormKey(k => k + 1);
    setDiagnosisModal(true);
  };

  // 提交诊断并完成就诊
  const submitDiagnosis = async (values) => {
    if (!currentAppt) return;
    setSubmitting(true);
    try {
      await diagnosisAPI.create({
        appointment_id: currentAppt.id,
        chief_complaint: values.chief_complaint || "",
        present_illness: values.present_illness || "",
        physical_examination: values.physical_examination || "",
        diagnosis: values.diagnosis,
        treatment_plan: values.treatment_plan || "",
        follow_up_date: values.follow_up_date ? values.follow_up_date.format("YYYY-MM-DD") : null,
      });
      await appointmentAPI.updateStatus(currentAppt.id, { status: "completed" });
      message.success("诊疗记录已创建，就诊完成");
      setDiagnosisModal(false);
      setCurrentAppt(null);
      loadAppointments();
    } catch (err) { /* handled */ }
    setSubmitting(false);
  };

  const updateStatus = async (id, status) => {
    try {
      await appointmentAPI.updateStatus(id, { status });
      message.success("状态已更新");
      loadAppointments();
    } catch (err) { /* handled */ }
  };

  const statusColors = { pending: "orange", confirmed: "blue", completed: "green", cancelled: "red", missed: "gray" };
  const statusLabels = { pending: "待确认", confirmed: "已确认", completed: "已完成", cancelled: "已取消", missed: "未到诊" };
  const slotLabels = { morning: "上午(8-12点)", afternoon: "下午(13-17点)", evening: "晚上(18-21点)" };

  const columns = [
    { title: "患者姓名", dataIndex: "patient_name", key: "patient_name", fixed: "left" },
    { title: "就诊日期", dataIndex: "appointment_date", key: "appointment_date" },
    { title: "时段", dataIndex: "time_slot", key: "time_slot", render: (v) => slotLabels[v] || v },
    { title: "排队号", dataIndex: "queue_number", key: "queue_number", render: (v) => <Tag color="blue" style={{ fontSize: 14 }}>{v}号</Tag> },
    { title: "症状描述", dataIndex: "symptoms", key: "symptoms", ellipsis: true, width: 200 },
    { title: "状态", dataIndex: "status", key: "status", render: (v) => <Tag color={statusColors[v]}>{statusLabels[v] || v}</Tag> },
    { title: "操作", key: "action", fixed: "right", width: 200,
      render: (_, r) => (
        <Space>
          {(r.status === "confirmed") && (
            <Button type="primary" size="small" icon={<CheckCircleOutlined />} onClick={() => openDiagnosis(r)}>
              完成就诊
            </Button>
          )}
          {r.status === "pending" && (
            <Button type="primary" size="small" ghost onClick={() => updateStatus(r.id, "confirmed")}>
              确认接诊
            </Button>
          )}
          {(r.status === "pending" || r.status === "confirmed") && (
            <Button danger size="small" icon={<CloseCircleOutlined />} onClick={() => updateStatus(r.id, "cancelled")}>
              取消
            </Button>
          )}
        </Space>
      ),
    },
  ];

  if (error) return <Alert message={error} type="warning" showIcon style={{ margin: 24 }} />;

  return (
    <div>
      <div className="page-header">
        <h3><CalendarOutlined /> 预约管理</h3>
        <p style={{ color: "#666", margin: 0 }}>管理您的患者预约，确认接诊或完成就诊并记录诊疗信息</p>
      </div>

      {doctor && (
        <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
          <Col xs={12} sm={6}><Card className="stat-card"><Statistic title="总预约" value={stats.total} prefix={<CalendarOutlined />} valueStyle={{ color: "#1677ff" }} /></Card></Col>
          <Col xs={12} sm={6}><Card className="stat-card"><Statistic title="待处理" value={stats.pending} prefix={<TeamOutlined />} valueStyle={{ color: "#faad14" }} /></Card></Col>
          <Col xs={12} sm={6}><Card className="stat-card"><Statistic title="已完成" value={stats.completed} prefix={<CheckCircleOutlined />} valueStyle={{ color: "#52c41a" }} /></Card></Col>
          <Col xs={12} sm={6}><Card className="stat-card"><Statistic title="已取消" value={stats.cancelled} prefix={<CloseCircleOutlined />} valueStyle={{ color: "#ff4d4f" }} /></Card></Col>
        </Row>
      )}

      <Card
        title={`预约列表 (${dateFilter || "全部"})`}
        extra={
          <Space>
            <DatePicker value={dateFilter ? dayjs(dateFilter) : null} onChange={(d) => setDateFilter(d ? d.format("YYYY-MM-DD") : null)} />
            <Select allowClear placeholder="筛选状态" value={statusFilter} onChange={setStatusFilter} style={{ width: 120 }}
              options={[{ value: "pending", label: "待确认" }, { value: "confirmed", label: "已确认" }, { value: "completed", label: "已完成" }, { value: "cancelled", label: "已取消" }]} />
            <Button icon={<ReloadOutlined />} onClick={loadAppointments}>刷新</Button>
          </Space>
        }
      >
        <Table dataSource={appointments} columns={columns} rowKey="id" loading={loading}
          size="middle" scroll={{ x: 900 }} pagination={{ pageSize: 20 }}
          locale={{ emptyText: <Empty description="暂无预约记录" /> }} />
      </Card>

      {/* 诊断表单弹窗 */}
      <Modal title={<><MedicineBoxOutlined /> 填写诊疗记录</>} open={diagnosisModal}
        onCancel={() => { setDiagnosisModal(false); setCurrentAppt(null); }} footer={null} width={640}
        destroyOnClose={true}>
        <Form layout="vertical" onFinish={submitDiagnosis}
          key={formKey}
          initialValues={{ chief_complaint: currentAppt?.symptoms || "" }}>
          <Form.Item name="chief_complaint" label="主诉">
            <Input.TextArea rows={2} placeholder="患者自述的主要症状和不适" />
          </Form.Item>
          <Form.Item name="present_illness" label="现病史">
            <Input.TextArea rows={2} placeholder="发病经过、诊疗过程等" />
          </Form.Item>
          <Form.Item name="physical_examination" label="体格检查">
            <Input.TextArea rows={2} placeholder="查体结果，如生命体征、专科检查等" />
          </Form.Item>
          <Form.Item name="diagnosis" label="诊断结果" rules={[{ required: true, message: "请输入诊断结果" }]}>
            <Input.TextArea rows={2} placeholder="诊断结论（必填）" />
          </Form.Item>
          <Form.Item name="treatment_plan" label="治疗方案">
            <Input.TextArea rows={2} placeholder="治疗建议、用药方案等" />
          </Form.Item>
          <Form.Item name="follow_up_date" label="复诊日期">
            <DatePicker style={{ width: "100%" }} />
          </Form.Item>
          <Button type="primary" htmlType="submit" loading={submitting} block size="large">
            保存诊疗记录并完成就诊
          </Button>
        </Form>
      </Modal>
    </div>
  );
}
