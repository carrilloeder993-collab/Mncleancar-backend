-- =============================================
-- MN Clean Car - Supabase Schema
-- Pega esto en: Supabase > SQL Editor > Run
-- =============================================

-- USUARIOS
create table if not exists users (
  id uuid primary key,
  phone text unique not null,
  password_hash text not null,
  name text not null,
  role text not null default 'client', -- 'client' | 'admin'
  created_at timestamptz default now()
);

-- SERVICIOS
create table if not exists services (
  id uuid primary key,
  name text not null,
  price numeric not null,
  includes text[] not null default '{}',
  active boolean not null default true,
  created_at timestamptz default now()
);

-- CITAS
create table if not exists bookings (
  id uuid primary key,
  user_id uuid references users(id),
  service_id uuid references services(id),
  date text not null,
  hour integer not null,
  vehicle_type text not null,
  address text not null,
  coupon_code text,
  final_price numeric not null default 0,
  status text not null default 'pending', -- pending | confirmed | completed | rejected
  created_at timestamptz default now()
);

-- CUPONES
create table if not exists coupons (
  id uuid primary key,
  code text unique not null,
  type text not null, -- discount_percent | discount_amount | free_service | loyalty_full
  value numeric not null default 0,
  assigned_to_phone text,
  note text,
  used boolean not null default false,
  used_by_phone text,
  is_loyalty boolean not null default false,
  created_at timestamptz default now()
);

-- EGRESOS
create table if not exists expenses (
  id uuid primary key,
  product_name text not null,
  cost numeric not null,
  quantity text not null,
  services_yield integer not null default 0,
  category text not null default 'producto', -- producto | gasolina | otro
  created_at timestamptz default now()
);

-- =============================================
-- USUARIO ADMIN INICIAL
-- =============================================
insert into users (id, phone, password_hash, name, role)
values (
  gen_random_uuid(),
  '8717958646',
  '$2b$12$4lljLLIKgjy1myYrJC1.GOYoWfBAXFTOXZTzbu7F5z4WfmezHQrq6',
  'Administrador',
  'admin'
) on conflict do nothing;

-- SERVICIOS DE EJEMPLO
insert into services (id, name, price, includes, active) values
  (gen_random_uuid(), 'Lavado Exterior', 80, ARRAY['Prelavado', 'Lavado de contacto', 'Enjuague', 'Secado'], true),
  (gen_random_uuid(), 'Lavado Completo', 150, ARRAY['Prelavado', 'Lavado exterior', 'Aspirado interior', 'Limpieza de tablero', 'Aromas'], true),
  (gen_random_uuid(), 'Pulido y Encerado', 300, ARRAY['Lavado completo', 'Pulido a máquina', 'Encerado protector', 'Brillado de llantas'], true)
on conflict do nothing;
