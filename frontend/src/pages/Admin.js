import React, { useState, useEffect } from 'react';
import { Table, Space, Button, message, Typography } from 'antd';
import axios from 'axios';

const { Title } = Typography;

function Admin() {
  const [posts, setPosts] = useState([]);

  useEffect(() => {
    fetchPosts();
  }, []);

  const fetchPosts = async () => {
    try {
      const response = await axios.get('http://localhost:5000/api/posts');
      setPosts(response.data);
    } catch (error) {
      message.error('获取数据失败');
    }
  };

  const handleDelete = async (id) => {
    try {
      await axios.delete(`http://localhost:5000/api/posts/${id}`);
      message.success('删除成功');
      fetchPosts();
    } catch (error) {
      message.error('删除失败');
    }
  };

  const columns = [
    {
      title: '标题',
      dataIndex: 'title',
      key: 'title',
    },
    {
      title: '平台',
      dataIndex: 'platform',
      key: 'platform',
    },
    {
      title: '账号',
      dataIndex: 'account_name',
      key: 'account_name',
    },
    {
      title: '发布者',
      dataIndex: 'author',
      key: 'author',
    },
    {
      title: '发布时间',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (text) => new Date(text).toLocaleDateString(),
    },
    {
      title: '操作',
      key: 'action',
      render: (_, record) => (
        <Space size="middle">
          <Button type="primary" onClick={() => handleEdit(record.id)}>
            编辑
          </Button>
          <Button type="danger" onClick={() => handleDelete(record.id)}>
            删除
          </Button>
        </Space>
      ),
    },
  ];

  return (
    <div>
      <Title level={2}>管理后台</Title>
      <Table columns={columns} dataSource={posts} rowKey="id" />
    </div>
  );
}

export default Admin;
