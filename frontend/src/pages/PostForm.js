import React, { useState } from 'react';
import { Form, Input, Button, message } from 'antd';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

const { TextArea } = Input;

function PostForm() {
  const [form] = Form.useForm();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);

  const onFinish = async (values) => {
    setLoading(true);
    try {
      await axios.post('http://localhost:5000/api/posts', values);
      message.success('发布成功！');
      navigate('/');
    } catch (error) {
      message.error('发布失败：' + (error.response?.data?.error || error.message));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: 600, margin: '0 auto', padding: '24px' }}>
      <h2>发布公益账号</h2>
      <Form
        form={form}
        layout="vertical"
        onFinish={onFinish}
      >
        <Form.Item
          name="title"
          label="标题"
          rules={[{ required: true, message: '请输入标题' }]}
        >
          <Input placeholder="请输入标题" />
        </Form.Item>

        <Form.Item
          name="platform"
          label="平台"
          rules={[{ required: true, message: '请输入平台名称' }]}
        >
          <Input placeholder="例如：微博、抖音、小红书等" />
        </Form.Item>

        <Form.Item
          name="account_name"
          label="账号名称"
          rules={[{ required: true, message: '请输入账号名称' }]}
        >
          <Input placeholder="请输入账号名称" />
        </Form.Item>

        <Form.Item
          name="content"
          label="账号介绍"
          rules={[{ required: true, message: '请输入账号介绍' }]}
        >
          <TextArea
            rows={4}
            placeholder="请详细介绍该公益账号的主要内容和影响力"
          />
        </Form.Item>

        <Form.Item>
          <Button type="primary" htmlType="submit" loading={loading} block>
            发布
          </Button>
        </Form.Item>
      </Form>
    </div>
  );
}

export default PostForm;
