import React from 'react';
import { Menu } from 'antd';
import { Link, useLocation } from 'react-router-dom';
import { HomeOutlined, PlusOutlined, SettingOutlined } from '@ant-design/icons';

function Navigation() {
  const location = useLocation();

  return (
    <Menu
      theme="dark"
      mode="horizontal"
      selectedKeys={[location.pathname]}
      style={{ lineHeight: '64px' }}
    >
      <Menu.Item key="/" icon={<HomeOutlined />}>
        <Link to="/">首页</Link>
      </Menu.Item>
      <Menu.Item key="/create-post" icon={<PlusOutlined />}>
        <Link to="/create-post">发布账号</Link>
      </Menu.Item>
      <Menu.Item key="/admin" icon={<SettingOutlined />}>
        <Link to="/admin">管理后台</Link>
      </Menu.Item>
    </Menu>
  );
}

export default Navigation;
