import React, { useState, useEffect } from "react";
import { Table, Card, Tag, Button, Modal, Input, message, Space, Spin } from "antd";
import { CloseCircleOutlined, ReloadOutlined, EyeOutlined } from "@ant-design/icons";
import { appointmentAPI } from "../../api";

export default function MyAppointments() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [cancelModal, setCancelModal] = useState(false);
  const [selectedId, setSelectedId] = useState(null);

  useEffect(() => { loadData(); }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const res = await appointmentAPI.getMy({ page: 1, size: 50 });
      setData(res.data.items || []);
    } catch (err) { /* handled */ }
    setLoading(false);
  };

  const handleCancel = () => {
    if (!selectedId) return;
    appointmentAPI.cancel(selectedId)
      .then(() => { message.success("已取消挂号"); setCancelModal(false); loadData(); })
      .catch(() => {});
  };

  const statusColors = { pending: "orange", confirmed: "blue", completed: "green", cancelled: "red", missed: "gray" };
  const statusLabels = { pending: "待确认", confirmed: "已确认", completed: "已完成", cancelled: "已取消", missed: "未到诊" };
  const slotLabels = { morning: "上午", afternoon: "下午", evening: "晚上" };

  const columns = [
    { title: "医生", dataIndex: "doctor_name", key: "doctor_name" },
    { title: "职称", dataIndex: "doctor_title", key: "doctor_title" },
    { title: "科室", dataIndex: "department_name", key: "department_name" },
    { title: "日期", dataIndex: "appointment_date", key: "appointment_date" },
    { title: "时段", dataIndex: "time_slot", key: "time_slot", render: (v) => slotLabels[v] || v },
    { title: "排队号", dataIndex: "queue_number", key: "queue_number", render: (v) => <Tag color="blue" style={{ fontSize: 16, fontWeight: "bold" }}>{v}</Tag> },
    { title: "状态", dataIndex: "status", key: "status", render: (v) => <Tag color={statusColors[v]}>{statusLabels[v] || v}</Tag> },
    { title: "操作", key: "action", render: (_, r) => (
      <Space>
        {["pending", "confirmed"].includes(r.status) && (
          <Button danger size="small" icon={<CloseCircleOutlined />}
            onClick={() => { setSelectedId(r.id); setCancelModal(true); }}>取消</Button>
        )}
      </Space>
    )},
  ];

  if (loading) return <Spin size="large" style={{ display: "block", textAlign: "center", marginTop: 100 }} />;

  return (
    <div>
      <div className="page-header"><h3>我的挂号记录</h3></div>
      <Card>
        <Space style={{ marginBottom: 16 }}>
          <Button icon={<ReloadOutlined />} onClick={loadData}>刷新</Button>
        </Space>
        <Table dataSource={data} columns={columns} rowKey="id" size="small" scroll={{ x: 600 }} />
      </Card>
      <Modal title="取消挂号" open={cancelModal} onOk={handleCancel} onCancel={() => setCancelModal(false)} okText="确认取消" cancelText="返回">
        <p>确定要取消该挂号记录吗？取消后无法恢复。</p>
      </Modal>
    </div>
  );
}
