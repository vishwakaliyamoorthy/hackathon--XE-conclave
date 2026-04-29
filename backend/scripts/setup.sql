-- 1. Enable Required Extensions
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 2. Create Users Table
CREATE TABLE IF NOT EXISTS public.users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    full_name TEXT,
    organization TEXT,
    role TEXT DEFAULT 'dev',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. Create Documents Table
CREATE TABLE IF NOT EXISTS public.documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES public.users(id),
    org_id TEXT,
    doc_type TEXT NOT NULL, -- 'prd', 'design', 'code'
    title TEXT NOT NULL,
    description TEXT,
    file_path TEXT,
    file_url TEXT,
    file_size INTEGER,
    raw_text TEXT,
    status TEXT DEFAULT 'uploaded',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. Create Analyses Table
CREATE TABLE IF NOT EXISTS public.analyses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES public.users(id),
    org_id TEXT,
    title TEXT NOT NULL,
    description TEXT,
    status TEXT DEFAULT 'pending', 
    prd_doc_id UUID REFERENCES public.documents(id),
    design_doc_id UUID REFERENCES public.documents(id),
    code_doc_id UUID REFERENCES public.documents(id),
    results JSONB,
    consistency_score INTEGER,
    total_conflicts INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

-- 5. Create Versions Table
CREATE TABLE IF NOT EXISTS public.versions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID REFERENCES public.documents(id) ON DELETE CASCADE,
    version_number INTEGER NOT NULL,
    content TEXT NOT NULL,
    changes TEXT,
    updated_by TEXT DEFAULT 'AI',
    timestamp TIMESTAMPTZ DEFAULT NOW()
);

-- 6. Setup Access
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.analyses ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.versions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow all" ON public.users FOR ALL USING (true);
CREATE POLICY "Allow all" ON public.documents FOR ALL USING (true);
CREATE POLICY "Allow all" ON public.analyses FOR ALL USING (true);
CREATE POLICY "Allow all" ON public.versions FOR ALL USING (true);
