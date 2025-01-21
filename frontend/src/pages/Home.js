import React, { useState, useEffect } from 'react';
import { Card, Row, Col, Typography, Space, Empty, Spin, message } from 'antd';
import { GlobalOutlined, UserOutlined } from '@ant-design/icons';
import axios from 'axios';

const { Title, Text, Paragraph } = Typography;

function Home() {
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchPosts();
  }, []);

  const fetchPosts = async () => {
    try {
      const response = await axios.get('http://localhost:5000/api/posts');
      setPosts(response.data);
    } catch (error) {
      message.error('获取数据失败：' + error.message);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '50px' }}>
        <Spin size="large" />
      </div>
    );
  }

  return (
    <div style={{ padding: '24px' }}>
      <Title level={2} style={{ marginBottom: '24px', textAlign: 'center' }}>
        公益账号分享平台
      </Title>
      {posts.length === 0 ? (
        <Empty description="暂无公益账号信息" />
      ) : (
        <Row gutter={[16, 16]}>
          {posts.map((post) => (
            <Col xs={24} sm={12} md={8} lg={6} key={post.id}>
              <Card
                title={post.title}
                hoverable
                style={{ height: '100%' }}
                actions={[
                  <Space>
                    <GlobalOutlined />
                    {post.platform}
                  </Space>,
                  <Space>
                    <UserOutlined />
                    {post.author}
                  </Space>
                ]}
              >
                <Space direction="vertical" style={{ width: '100%' }}>
                  <Text strong>账号：{post.account_name}</Text>
                  <Paragraph ellipsis={{ rows: 3 }}>{post.content}</Paragraph>
                  <Text type="secondary" style={{ fontSize: '12px' }}>
                    发布时间：{new Date(post.created_at).toLocaleDateString()}
                  </Text>
                </Space>
              </Card>
            </Col>
          ))}
        </Row>
      )}
    </div>
  );
}

export default Home;
