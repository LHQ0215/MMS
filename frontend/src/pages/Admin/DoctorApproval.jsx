import React, { useState, useEffect } from "react";
import { Table, Card, Tag, Button, Space, message, Modal, Descriptions } from "antd";
import { CheckCircleOutlined, CloseCircleOutlined, ReloadOutlined } from "@ant-design/icons";
import { doctorAPI } from "../../api";

export default function DoctorApproval() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [detail, setDetail] = useState(null);

  useEffect(() => { loadData(); }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const res = await doctorAPI.list({ page: 1, size: 100 });
      setData(res.data.items || []);
    } catch (err) { /* handled */ }
    setLoading(false);
  };

  const handleApprove = async (doctorId, approved) => {
    try {
      // We can get the actual doctor id from backend call
      await doctorAPI.approve(doctorId);
      message.success(approved ? "已通过审核" : "已取消审核");
      loadData();
    } catch (err) { /* handled */ }
  };

  const columns = [
    { title: "姓名", dataIndex: "real_name", key: "real_name" },
    { title: "职称", dataIndex: "title", key: "title" },
    { title: "科室", dataIndex: "department_name", key: "department_name" },
    { title: "专业特长", dataIndex: "specialization", key: "specialization", ellipsis: true },
    { title: "手机", dataIndex: "phone", key: "phone" },
    { title: "状态", key: "is_approved",
      render: (_, r) => r.is_approved ? <Tag color="green">已通过</Tag> : <Tag color="orange">待审核</Tag> },
    { title: "操作", key: "action",
      render: (_, r) => (
        <Space>
          {!r.is_approved && <Button type="primary" size="small" icon={<CheckCircleOutlined />} onClick={() => handleApprove(r.id, true)}>通过</Button>}
          {r.is_approved && <Button danger size="small" icon={<CloseCircleOutlined />} onClick={() => handleApprove(r.id, false)}>取消审核</Button>}
        </Space>
      )},
  ];

  return (
    <div>
      <div className="page-header"><h3>医师审核</h3></div>
      <Card>
        <Space style={{ marginBottom: 16 }}>
          <Button icon={<ReloadOutlined />} onClick={loadData}>刷新</Button>
        </Space>
        <Table dataSource={data} columns={columns} rowKey="id" loading={loading} size="small" />
      </Card>
    </div>
  );
}
