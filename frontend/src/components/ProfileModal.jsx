import React, { useState, useEffect, useRef } from "react";
import { Modal, Descriptions, Tag, Button, Form, Input, Select, DatePicker, InputNumber, message, Spin, Space } from "antd";
import { UserOutlined, EditOutlined } from "@ant-design/icons";
import { userAPI, doctorAPI, patientAPI } from "../api";
import dayjs from "dayjs";

export default function ProfileModal({ open, onClose }) {
  const [userInfo, setUserInfo] = useState(null);
  const [profileInfo, setProfileInfo] = useState(null);
  const [loading, setLoading] = useState(false);
  const [editing, setEditing] = useState(false);
  const [saving, setSaving] = useState(false);
  const role = userInfo?.role;
  const [form] = Form.useForm();
  const prevOpen = useRef(false);

  useEffect(() => {
    if (open && !prevOpen.current) {
      setEditing(false);
      form.resetFields();
      loadProfile();
    }
    prevOpen.current = open;
  }, [open]);

  const loadProfile = async () => {
    setLoading(true);
    try {
      const userRes = await userAPI.getMe();
      setUserInfo(userRes.data);
      if (userRes.data.role === "doctor") {
        try {
          const docRes = await doctorAPI.getProfile();
          setProfileInfo(docRes.data);
        } catch (e) { setProfileInfo(null); }
      } else if (userRes.data.role === "patient") {
        try {
          const patRes = await patientAPI.getProfile();
          setProfileInfo(patRes.data);
        } catch (e) { setProfileInfo(null); }
      }
    } catch (err) { /* handled */ }
    setLoading(false);
  };

  const handleEdit = () => {
    form.setFieldsValue({
      real_name: userInfo?.real_name || "",
      phone: userInfo?.phone || "",
      email: userInfo?.email || "",
    });
    if (role === "patient" && profileInfo) {
      form.setFieldsValue({
        gender: profileInfo?.gender || undefined,
        birth_date: profileInfo?.birth_date ? dayjs(profileInfo.birth_date) : undefined,
        address: profileInfo?.address || "",
        height: profileInfo?.height ?? null,
        weight: profileInfo?.weight ?? null,
        allergies: profileInfo?.allergies || "",
        medical_history: profileInfo?.medical_history || "",
        emergency_contact: profileInfo?.emergency_contact || "",
        emergency_phone: profileInfo?.emergency_phone || "",
      });
    }
    if (role === "doctor" && profileInfo) {
      form.setFieldsValue({
        title: profileInfo?.title || undefined,
        specialization: profileInfo?.specialization || "",
        consultation_fee: profileInfo?.consultation_fee ?? null,
        max_daily_patients: profileInfo?.max_daily_patients ?? 30,
        introduction: profileInfo?.introduction || "",
      });
    }
    setEditing(true);
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      const vals = form.getFieldsValue();

      // Save base user info
      await userAPI.updateMe({
        real_name: vals.real_name,
        phone: vals.phone,
        email: vals.email,
      });

      // Save role-specific info
      if (role === "patient") {
        const patData = {
          gender: vals.gender,
          birth_date: vals.birth_date ? vals.birth_date.format("YYYY-MM-DD") : undefined,
          address: vals.address || undefined,
          height: vals.height != null ? Number(vals.height) : undefined,
          weight: vals.weight != null ? Number(vals.weight) : undefined,
          allergies: vals.allergies || undefined,
          medical_history: vals.medical_history || undefined,
          emergency_contact: vals.emergency_contact || undefined,
          emergency_phone: vals.emergency_phone || undefined,
        };
        Object.keys(patData).forEach(k => { if (patData[k] === undefined) delete patData[k]; });
        if (Object.keys(patData).length > 0) await patientAPI.updateProfile(patData);
      }
      if (role === "doctor") {
        const docData = {
          title: vals.title || undefined,
          specialization: vals.specialization || undefined,
          consultation_fee: vals.consultation_fee != null ? Number(vals.consultation_fee) : undefined,
          max_daily_patients: vals.max_daily_patients != null ? Number(vals.max_daily_patients) : undefined,
          introduction: vals.introduction || undefined,
        };
        Object.keys(docData).forEach(k => { if (docData[k] === undefined) delete docData[k]; });
        if (Object.keys(docData).length > 0) await doctorAPI.updateProfile(docData);
      }

      message.success("个人信息已更新");
      setEditing(false);
      loadProfile();
    } catch (err) { /* handled */ }
    setSaving(false);
  };

  const roleLabels = { admin: "管理员", doctor: "医生", patient: "患者" };
  const roleColors = { admin: "red", doctor: "blue", patient: "green" };

  return (
    <Modal title={<><UserOutlined /> 个人信息</>} open={open}
      onCancel={() => { setEditing(false); onClose(); }}
      footer={editing ? (
        <Space>
          <Button onClick={() => setEditing(false)}>取消</Button>
          <Button type="primary" loading={saving} onClick={handleSave}>保存</Button>
        </Space>
      ) : (
        <Button type="primary" icon={<EditOutlined />} onClick={handleEdit}>编辑信息</Button>
      )} width={640} destroyOnClose={false}>
      {loading ? <Spin style={{ display: "block", margin: "40px auto" }} /> : !editing ? (
        <Descriptions column={1} bordered size="small">
          <Descriptions.Item label="用户名">{userInfo?.username}</Descriptions.Item>
          <Descriptions.Item label="姓名">{userInfo?.real_name}</Descriptions.Item>
          <Descriptions.Item label="角色">
            <Tag color={roleColors[role]}>{roleLabels[role] || role}</Tag>
          </Descriptions.Item>
          <Descriptions.Item label="手机号">{userInfo?.phone || "未设置"}</Descriptions.Item>
          <Descriptions.Item label="邮箱">{userInfo?.email || "未设置"}</Descriptions.Item>
          <Descriptions.Item label="状态">
            <Tag color={userInfo?.is_active ? "green" : "red"}>{userInfo?.is_active ? "正常" : "已禁用"}</Tag>
          </Descriptions.Item>
          {role === "doctor" && profileInfo && (
            <>
              <Descriptions.Item label="职称">{profileInfo?.title}</Descriptions.Item>
              <Descriptions.Item label="所属科室">{profileInfo?.department_name}</Descriptions.Item>
              <Descriptions.Item label="专业特长">{profileInfo?.specialization || "无"}</Descriptions.Item>
              <Descriptions.Item label="执业证号">{profileInfo?.license_number}</Descriptions.Item>
              <Descriptions.Item label="挂号费">{profileInfo?.consultation_fee ? `¥${profileInfo.consultation_fee}` : "未设置"}</Descriptions.Item>
              <Descriptions.Item label="每日最大接诊数">{profileInfo?.max_daily_patients || "未设置"}</Descriptions.Item>
              <Descriptions.Item label="个人简介">{profileInfo?.introduction || "无"}</Descriptions.Item>
              <Descriptions.Item label="审核状态">
                <Tag color={profileInfo?.is_approved ? "green" : "orange"}>{profileInfo?.is_approved ? "已通过" : "待审核"}</Tag>
              </Descriptions.Item>
            </>
          )}
          {role === "patient" && profileInfo && (
            <>
              <Descriptions.Item label="性别">{profileInfo?.gender === "male" ? "男" : profileInfo?.gender === "female" ? "女" : "未设置"}</Descriptions.Item>
              <Descriptions.Item label="出生日期">{profileInfo?.birth_date || "未设置"}</Descriptions.Item>
              <Descriptions.Item label="地址">{profileInfo?.address || "未设置"}</Descriptions.Item>
              <Descriptions.Item label="身高(cm)">{profileInfo?.height ?? "未设置"}</Descriptions.Item>
              <Descriptions.Item label="体重(kg)">{profileInfo?.weight ?? "未设置"}</Descriptions.Item>
              <Descriptions.Item label="血型">{profileInfo?.blood_type || "未设置"}</Descriptions.Item>
              <Descriptions.Item label="过敏史">{profileInfo?.allergies || "无"}</Descriptions.Item>
              <Descriptions.Item label="既往病史">{profileInfo?.medical_history || "无"}</Descriptions.Item>
              <Descriptions.Item label="紧急联系人">{profileInfo?.emergency_contact || "未设置"}</Descriptions.Item>
              <Descriptions.Item label="紧急联系电话">{profileInfo?.emergency_phone || "未设置"}</Descriptions.Item>
            </>
          )}
        </Descriptions>
      ) : (
        <Form form={form} layout="vertical" style={{ maxHeight: 460, overflow: "auto" }}>
          <h4 style={{ marginBottom: 12 }}>基本信息</h4>
          <Form.Item name="real_name" label="姓名"><Input /></Form.Item>
          <Form.Item name="phone" label="手机号"><Input placeholder="请输入手机号" /></Form.Item>
          <Form.Item name="email" label="邮箱"><Input placeholder="请输入邮箱" /></Form.Item>

          {role === "patient" && (
            <>
              <h4 style={{ marginTop: 16, marginBottom: 12 }}>患者信息</h4>
              <Form.Item name="gender" label="性别">
                <Select options={[{ value: "male", label: "男" }, { value: "female", label: "女" }, { value: "other", label: "其他" }]} allowClear />
              </Form.Item>
              <Form.Item name="birth_date" label="出生日期"><DatePicker style={{ width: "100%" }} /></Form.Item>
              <Form.Item name="address" label="地址"><Input placeholder="请输入家庭住址" /></Form.Item>
              <Form.Item name="height" label="身高(cm)"><InputNumber min={0} max={250} style={{ width: "100%" }} placeholder="如：170" /></Form.Item>
              <Form.Item name="weight" label="体重(kg)"><InputNumber min={0} max={300} style={{ width: "100%" }} placeholder="如：65" /></Form.Item>
              <Form.Item name="allergies" label="过敏史"><Input.TextArea rows={2} placeholder="请填写过敏药物或食物" /></Form.Item>
              <Form.Item name="medical_history" label="既往病史"><Input.TextArea rows={2} placeholder="请填写既往疾病史" /></Form.Item>
              <Form.Item name="emergency_contact" label="紧急联系人"><Input placeholder="紧急联系人姓名" /></Form.Item>
              <Form.Item name="emergency_phone" label="紧急联系电话"><Input placeholder="紧急联系人电话" /></Form.Item>
            </>
          )}

          {role === "doctor" && (
            <>
              <h4 style={{ marginTop: 16, marginBottom: 12 }}>医生信息</h4>
              <Form.Item name="title" label="职称">
                <Select options={[
                  { value: "主任医师", label: "主任医师" }, { value: "副主任医师", label: "副主任医师" },
                  { value: "主治医师", label: "主治医师" }, { value: "住院医师", label: "住院医师" }, { value: "医士", label: "医士" }
                ]} />
              </Form.Item>
              <Form.Item name="specialization" label="专业特长"><Input placeholder="如：心血管疾病、消化系统疾病" /></Form.Item>
              <Form.Item name="consultation_fee" label="挂号费(元)"><InputNumber min={0} precision={2} style={{ width: "100%" }} placeholder="如：20" /></Form.Item>
              <Form.Item name="max_daily_patients" label="每日最大接诊数"><InputNumber min={1} max={200} style={{ width: "100%" }} /></Form.Item>
              <Form.Item name="introduction" label="个人简介"><Input.TextArea rows={3} placeholder="请介绍您的专业背景和擅长领域" /></Form.Item>
            </>
          )}
        </Form>
      )}
    </Modal>
  );
}
