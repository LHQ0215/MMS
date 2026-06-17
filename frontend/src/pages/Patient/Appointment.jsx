import React, { useState, useEffect } from "react";
import { Card, Form, Select, DatePicker, Input, Button, message, Alert, Spin, Descriptions, Row, Col } from "antd";
import { CalendarOutlined, MedicineBoxOutlined } from "@ant-design/icons";
import { doctorAPI, departmentAPI, appointmentAPI } from "../../api";
import dayjs from "dayjs";

export default function PatientAppointment() {
  const [form] = Form.useForm();
  const [departments, setDepartments] = useState([]);
  const [doctors, setDoctors] = useState([]);
  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [selectedDept, setSelectedDept] = useState(null);

  useEffect(() => {
    loadDepartments();
  }, []);

  const loadDepartments = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await departmentAPI.list();
      setDepartments(res.data.items || []);
    } catch (err) {
      setError("无法加载科室信息，请确保后端服务已启动");
    }
    setLoading(false);
  };

  const loadDoctors = async (deptId) => {
    try {
      const res = await doctorAPI.list({ department_id: deptId, page: 1, size: 50 });
      setDoctors(res.data.items || []);
    } catch (err) { /* handled */ }
  };

  const onDeptChange = (deptId) => {
    setSelectedDept(deptId);
    if (deptId) loadDoctors(deptId);
    else setDoctors([]);
    form.setFieldsValue({ doctor_id: undefined });
  };

  const onFinish = async (values) => {
    setSubmitting(true);
    try {
      const res = await appointmentAPI.create({
        doctor_id: values.doctor_id,
        department_id: values.department_id,
        appointment_date: values.appointment_date.format("YYYY-MM-DD"),
        time_slot: values.time_slot,
        symptoms: values.symptoms || "",
      });
      setResult(res.data);
      message.success("挂号成功！");
    } catch (err) { /* handled */ }
    setSubmitting(false);
  };

  if (loading) return <Spin size="large" style={{ display: "block", textAlign: "center", marginTop: 100 }} />;

  return (
    <div>
      {error && <Alert message={error} type="warning" showIcon style={{ marginBottom: 16 }} />}
      <div className="page-header"><h3>预约挂号 <CalendarOutlined /></h3></div>
      <Row gutter={24}>
        <Col xs={24} md={12}>
          <Card title="填写挂号信息">
            <Form form={form} layout="vertical" onFinish={onFinish}>
              <Form.Item name="department_id" label="选择科室" rules={[{ required: true, message: "请选择科室" }]}>
                <Select showSearch placeholder="请选择科室" onChange={onDeptChange}
                  options={departments.map(d => ({ value: d.id, label: d.name }))}
                  optionFilterProp="label" />
              </Form.Item>
              <Form.Item name="doctor_id" label="选择医生" rules={[{ required: true, message: "请选择医生" }]}>
                <Select showSearch placeholder={doctors.length ? "请选择医生" : "请先选择科室"}
                  options={doctors.map(d => ({ value: d.id, label: `${d.real_name} (${d.title}) - ¥${d.consultation_fee || 0}` }))}
                  optionFilterProp="label" disabled={!selectedDept} />
              </Form.Item>
              <Form.Item name="appointment_date" label="就诊日期" rules={[{ required: true, message: "请选择日期" }]}>
                <DatePicker style={{ width: "100%" }} disabledDate={(d) => d && d < dayjs().startOf("day")} />
              </Form.Item>
              <Form.Item name="time_slot" label="就诊时段" rules={[{ required: true, message: "请选择时段" }]}>
                <Select options={[{ value: "morning", label: "上午 (8:00-12:00)" }, { value: "afternoon", label: "下午 (13:00-17:00)" }, { value: "evening", label: "晚上 (18:00-21:00)" }]} />
              </Form.Item>
              <Form.Item name="symptoms" label="症状描述">
                <Input.TextArea rows={3} placeholder="请描述您的症状，方便医生提前了解" />
              </Form.Item>
              <Button type="primary" htmlType="submit" loading={submitting} block size="large">
                确认挂号
              </Button>
            </Form>
          </Card>
        </Col>
        <Col xs={24} md={12}>
          {result && (
            <Card title="挂号成功" style={{ background: "#f6ffed", borderColor: "#b7eb8f" }}>
              <Descriptions column={1}>
                <Descriptions.Item label="排队号"><span style={{ fontSize: 28, fontWeight: "bold", color: "#1677ff" }}>{result.queue_number}</span> 号</Descriptions.Item>
                <Descriptions.Item label="挂号ID">{result.appointment_id}</Descriptions.Item>
                <Descriptions.Item label="温馨提示">请按照预约时间提前15分钟到达医院，前往相应科室就诊。</Descriptions.Item>
              </Descriptions>
            </Card>
          )}
        </Col>
      </Row>
    </div>
  );
}
