import React, { useState, useEffect } from "react";
import { Table, Card, Tag, Button, Space, Input, message, Switch } from "antd";
import { SearchOutlined, ReloadOutlined } from "@ant-design/icons";
import { userAPI } from "../../api";

export default function UserManage() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [keyword, setKeyword] = useState("");

  useEffect(() => { loadData(); }, [page]);

  const loadData = async () => {
    setLoading(true);
    try {
      const res = await userAPI.list({ page, size: 20, keyword });
      setData(res.data.items || []);
      setTotal(res.data.total || 0);
    } catch (err) { /* handled */ }
    setLoading(false);
  };

  const toggleStatus = async (userId) => {
    try {
      await userAPI.toggleStatus(userId);
      message.success("状态已更新");
      loadData();
    } catch (err) { /* handled */ }
  };

  const columns = [
    { title: "ID", dataIndex: "id", key: "id", width: 60 },
    { title: "用户名", dataIndex: "username", key: "username" },
    { title: "姓名", dataIndex: "real_name", key: "real_name" },
    { title: "角色", dataIndex: "role", key: "role",
      render: (r) => ({ admin: <Tag color="red">管理员</Tag>, doctor: <Tag color="blue">医生</Tag>, patient: <Tag color="green">患者</Tag> })[r] || r },
    { title: "手机", dataIndex: "phone", key: "phone" },
    { title: "邮箱", dataIndex: "email", key: "email" },
    { title: "状态", dataIndex: "is_active", key: "is_active",
      render: (v, record) => <Switch checked={v} onChange={() => toggleStatus(record.id)} checkedChildren="正常" unCheckedChildren="禁用" /> },
    { title: "创建时间", dataIndex: "created_at", key: "created_at" },
  ];

  return (
    <div>
      <div className="page-header">
        <h3>用户管理</h3>
      </div>
      <Card>
        <Space style={{ marginBottom: 16 }}>
          <Input.Search placeholder="搜索用户" prefix={<SearchOutlined />} value={keyword}
            onChange={(e) => setKeyword(e.target.value)} onSearch={() => { setPage(1); loadData(); }}
            enterButton allowClear />
          <Button icon={<ReloadOutlined />} onClick={loadData}>刷新</Button>
        </Space>
        <Table dataSource={data} columns={columns} rowKey="id" loading={loading}
          pagination={{ current: page, total, pageSize: 20, onChange: setPage }} size="small" />
      </Card>
    </div>
  );
}
