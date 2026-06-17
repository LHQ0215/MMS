import React, { useState, useEffect } from "react";
import { Table, Card, Modal, Descriptions, Tag, Button, Space, Spin, Empty, Alert } from "antd";
import { EyeOutlined, ReloadOutlined, MedicineBoxOutlined, CalendarOutlined } from "@ant-design/icons";
import { diagnosisAPI, prescriptionAPI, appointmentAPI } from "../../api";

export default function DoctorRecords() {
  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [detail, setDetail] = useState(null);
  const [prescs, setPrescs] = useState([]);
  const [detailModal, setDetailModal] = useState(false);

  useEffect(() => { loadData(); }, []);

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      // 先获取正式诊疗记录
      const diagRes = await diagnosisAPI.getDoctor({ page: 1, size: 200 });
      let items = diagRes.data.items || [];

      // 如果正式记录为空，回退到已完成预约作为基础就诊记录
      if (items.length === 0) {
        try {
          const apptRes = await appointmentAPI.getDoctor({ page: 1, size: 200, status_filter: "completed" });
          const apptItems = (apptRes.data.items || []).map(a => ({
            id: `appt-${a.id}`,
            patient_name: a.patient_name,
            diagnosis: a.diagnosis || "待补充",
            chief_complaint: a.symptoms || "",
            treatment_plan: "",
            follow_up_date: null,
            created_at: a.appointment_date,
            _isAppointment: true,
            _appointmentId: a.id,
          }));
          items = apptItems;
        } catch (e) { /* no fallback */ }
      }

      setRecords(items);
    } catch (err) {
      setError("加载诊疗记录失败");
    }
    setLoading(false);
  };

  const viewDetail = async (record) => {
    if (record._isAppointment) {
      // 预约记录无详情，提示使用"完成就诊"填写正式记录
      setDetail(null);
      setPrescs([]);
      setDetailModal(true);
      return;
    }
    try {
      const [detailRes, prescRes] = await Promise.all([
        diagnosisAPI.get(record.id),
        prescriptionAPI.getByRecord(record.id).catch(() => ({ data: { items: [] } })),
      ]);
      setDetail(detailRes.data);
      setPrescs(prescRes.data.items || []);
      setDetailModal(true);
    } catch (err) { /* handled */ }
  };

  const columns = [
    { title: "患者姓名", dataIndex: "patient_name", key: "patient_name" },
    { title: "诊断结果", dataIndex: "diagnosis", key: "diagnosis", ellipsis: true },
    { title: "主诉/症状", dataIndex: "chief_complaint", key: "chief_complaint", ellipsis: true },
    { title: "就诊时间", dataIndex: "created_at", key: "created_at" },
    { title: "类型", key: "type", render: (_, r) => r._isAppointment
      ? <Tag icon={<CalendarOutlined />} color="default">预约记录</Tag>
      : <Tag color="blue">正式记录</Tag> },
    { title: "操作", key: "action", render: (_, r) => (
      <Button type="link" icon={<EyeOutlined />} onClick={() => viewDetail(r)}>查看详情</Button>
    )},
  ];

  return (
    <div>
      <div className="page-header"><h3>诊疗记录 <MedicineBoxOutlined /></h3></div>
      <Card>
        <Space style={{ marginBottom: 16 }}>
          <Button icon={<ReloadOutlined />} onClick={loadData}>刷新</Button>
        </Space>
        {error && <Alert message={error} type="error" showIcon closable style={{ marginBottom: 16 }} />}
        {records.length === 0 && !loading && !error ? (
          <Empty description="暂无诊疗记录" />
        ) : (
          <Table dataSource={records} columns={columns} rowKey="id" loading={loading} size="small" />
        )}
      </Card>
      <Modal title="就诊详情" open={detailModal} onCancel={() => {
        setDetailModal(false); setDetail(null);
      }} footer={null} width={640}>
        {detail ? (
          <>
            <Descriptions column={1} bordered size="small" style={{ marginBottom: 16 }}>
              <Descriptions.Item label="医生">{detail.doctor_name} ({detail.doctor_title})</Descriptions.Item>
              <Descriptions.Item label="患者">{detail.patient_name}</Descriptions.Item>
              <Descriptions.Item label="主诉">{detail.chief_complaint || "无"}</Descriptions.Item>
              <Descriptions.Item label="现病史">{detail.present_illness || "无"}</Descriptions.Item>
              <Descriptions.Item label="体格检查">{detail.physical_examination || "无"}</Descriptions.Item>
              <Descriptions.Item label="诊断结果"><Tag color="blue">{detail.diagnosis}</Tag></Descriptions.Item>
              <Descriptions.Item label="治疗方案">{detail.treatment_plan || "无"}</Descriptions.Item>
              <Descriptions.Item label="复诊日期">{detail.follow_up_date || "无需复诊"}</Descriptions.Item>
            </Descriptions>
            {prescs.length > 0 && (
              <Card title="处方信息" size="small">
                <Table dataSource={prescs} columns={[
                  { title: "药品", dataIndex: "medicine_name", key: "medicine_name" },
                  { title: "规格", dataIndex: "medicine_spec", key: "medicine_spec" },
                  { title: "用量", dataIndex: "dosage", key: "dosage" },
                  { title: "频次", dataIndex: "frequency", key: "frequency" },
                  { title: "疗程", dataIndex: "duration", key: "duration" },
                ]} rowKey="id" pagination={false} size="small" />
              </Card>
            )}
          </>
        ) : (
          <Empty description="此记录为已完成预约，尚未填写正式诊疗信息。请在「预约管理」中通过完成就诊流程填写完整记录。" />
        )}
      </Modal>
    </div>
  );
}
