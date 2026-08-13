// Mock Data cho Dashboard Analytics — thay thế API thật khi chưa có Backend

export interface KPIData {
  negativeRate: number;
  negativeRateDelta: number;
  feedbackVolume: number;
  feedbackVolumeDelta: number;
  activeHotspots: number;
  criticalHotspots: number;
  unknownRate: number;
  unknownRateDelta: number;
}

export interface JourneyStage {
  code: string;
  name: string;
  feedbackCount: number;
  negativeRate: number;
  trend: 'up' | 'down' | 'stable';
}

export interface TrendPoint {
  date: string;
  negativeRate: number;
  feedbackVolume: number;
  hotspotCount: number;
}

export interface PainPoint {
  rank: number;
  issueCode: string;
  issueName: string;
  serviceCode: string;
  serviceName: string;
  count: number;
  negativeRate: number;
  trend: number; // % thay đổi so với kỳ trước
  hasHotspot: boolean;
}

export interface HotspotRow {
  id: string;
  severity: 'SEV-1' | 'SEV-2' | 'SEV-3' | 'SEV-4';
  customerPain: string;
  serviceCode: string;
  issueCode: string;
  location: string;
  evidenceCount: number;
  trendPercent: number;
  status: 'INVESTIGATING' | 'CANDIDATE' | 'CONFIRMED' | 'RESOLVED';
  owner: string;
}

export interface JourneyStep {
  code: string;
  name: string;
  feedbackCount: number;
  negativeRate: number;
}

// ─── KPI ───────────────────────────────────────────────
export const mockKPI: KPIData = {
  negativeRate: 34.2,
  negativeRateDelta: -2.1,
  feedbackVolume: 18546,
  feedbackVolumeDelta: 8.4,
  activeHotspots: 7,
  criticalHotspots: 2,
  unknownRate: 7.4,
  unknownRateDelta: -0.8,
};

// ─── JOURNEY STAGES ─────────────────────────────────────
export const mockJourneyStages: JourneyStage[] = [
  { code: 'STG-01', name: 'Nhận thức', feedbackCount: 1200, negativeRate: 12, trend: 'down' },
  { code: 'STG-02', name: 'Xem xét', feedbackCount: 2100, negativeRate: 18, trend: 'stable' },
  { code: 'STG-03', name: 'Giao dịch', feedbackCount: 3400, negativeRate: 27, trend: 'up' },
  { code: 'STG-04', name: 'Nhận nhà', feedbackCount: 2600, negativeRate: 31, trend: 'up' },
  { code: 'STG-05', name: 'Cư trú', feedbackCount: 7400, negativeRate: 42, trend: 'up' },
  { code: 'STG-06', name: 'Vận hành', feedbackCount: 1846, negativeRate: 35, trend: 'down' },
];

// ─── TREND (30 ngày gần nhất) ───────────────────────────
export const mockTrend: TrendPoint[] = Array.from({ length: 30 }, (_, i) => {
  const date = new Date(2026, 6, 14 + i);
  const baseNeg = 34 + Math.sin(i / 3) * 6 + (Math.random() - 0.5) * 4;
  return {
    date: date.toISOString().slice(0, 10),
    negativeRate: Math.max(10, Math.min(60, baseNeg)),
    feedbackVolume: Math.floor(550 + Math.cos(i / 4) * 150 + Math.random() * 100),
    hotspotCount: Math.floor(5 + Math.sin(i / 5) * 3),
  };
});

// ─── TOP PAIN POINTS ────────────────────────────────────
export const mockPainPoints: PainPoint[] = [
  { rank: 1, issueCode: 'IS-05-02', issueName: 'Thang máy chờ lâu', serviceCode: 'SV-05', serviceName: 'Tiếp cận & Di chuyển', count: 1490, negativeRate: 78, trend: 180, hasHotspot: true },
  { rank: 2, issueCode: 'IS-02-01', issueName: 'Đăng nhập App / OTP', serviceCode: 'SV-02', serviceName: 'App & Hệ thống số', count: 1120, negativeRate: 65, trend: 75, hasHotspot: true },
  { rank: 3, issueCode: 'IS-06-03', issueName: 'Không ghi nhận thanh toán', serviceCode: 'SV-06', serviceName: 'Thanh toán & Phí', count: 860, negativeRate: 71, trend: 32, hasHotspot: false },
  { rank: 4, issueCode: 'IS-05-04', issueName: 'Lỗi thẻ từ / hầm xe', serviceCode: 'SV-05', serviceName: 'Tiếp cận & Di chuyển', count: 620, negativeRate: 58, trend: 15, hasHotspot: false },
  { rank: 5, issueCode: 'IS-07-01', issueName: 'Phí phát sinh không báo trước', serviceCode: 'SV-07', serviceName: 'Kỹ thuật & Tài sản', count: 540, negativeRate: 82, trend: -5, hasHotspot: false },
  { rank: 6, issueCode: 'IS-03-02', issueName: 'Không liên lạc được CSKH', serviceCode: 'SV-03', serviceName: 'Giao tiếp & CSKH', count: 410, negativeRate: 55, trend: -12, hasHotspot: false },
];

// ─── EMERGING HOTSPOTS ──────────────────────────────────
export const mockHotspots: HotspotRow[] = [
  { id: 'HS-001', severity: 'SEV-2', customerPain: 'Thang máy chờ quá lâu giờ cao điểm', serviceCode: 'SV-05', issueCode: 'IS-05-02', location: 'Tòa S2', evidenceCount: 42, trendPercent: 180, status: 'INVESTIGATING', owner: 'Kỹ thuật' },
  { id: 'HS-002', severity: 'SEV-3', customerPain: 'Không đăng nhập được App cư dân', serviceCode: 'SV-02', issueCode: 'IS-02-01', location: 'Toàn dự án', evidenceCount: 27, trendPercent: 75, status: 'CANDIDATE', owner: 'IT' },
  { id: 'HS-003', severity: 'SEV-3', customerPain: 'Thanh toán không được ghi nhận', serviceCode: 'SV-06', issueCode: 'IS-06-03', location: 'Tòa S1, S3', evidenceCount: 18, trendPercent: 32, status: 'CANDIDATE', owner: 'Tài chính' },
  { id: 'HS-004', severity: 'SEV-4', customerPain: 'Thẻ từ hầm xe bị lỗi', serviceCode: 'SV-05', issueCode: 'IS-05-04', location: 'Hầm B1', evidenceCount: 12, trendPercent: 15, status: 'CONFIRMED', owner: 'Bảo vệ' },
];

// ─── JOURNEY STEPS BY STAGE ─────────────────────────────
export const mockStageSteps: Record<string, JourneyStep[]> = {
  'STG-01': [ // Nhận thức
    { code: 'AWR-01', name: 'Tìm hiểu dự án & quảng cáo', feedbackCount: 450, negativeRate: 10 },
    { code: 'AWR-02', name: 'Tư vấn thông tin bán hàng', feedbackCount: 750, negativeRate: 14 },
  ],
  'STG-02': [ // Xem xét
    { code: 'CSD-01', name: 'Tham quan nhà mẫu', feedbackCount: 1100, negativeRate: 15 },
    { code: 'CSD-02', name: 'Thương lượng giá & chính sách', feedbackCount: 1000, negativeRate: 21 },
  ],
  'STG-03': [ // Giao dịch
    { code: 'TRN-01', name: 'Đặt cọc & ký hợp đồng', feedbackCount: 1800, negativeRate: 25 },
    { code: 'TRN-02', name: 'Thanh toán tiến độ', feedbackCount: 1600, negativeRate: 29 },
  ],
  'STG-04': [ // Nhận nhà
    { code: 'HOV-01', name: 'Nghiệm thu căn hộ', feedbackCount: 1400, negativeRate: 35 },
    { code: 'HOV-02', name: 'Bàn giao chìa khóa & hồ sơ', feedbackCount: 1200, negativeRate: 26 },
  ],
  'STG-05': [ // Cư trú
    { code: 'RES-01', name: 'Hồ sơ cư dân', feedbackCount: 640, negativeRate: 18 },
    { code: 'RES-02', name: 'App & hệ thống', feedbackCount: 1210, negativeRate: 44 },
    { code: 'RES-03', name: 'Ra vào & di chuyển', feedbackCount: 2140, negativeRate: 51 },
    { code: 'RES-04', name: 'Tiếp khách', feedbackCount: 520, negativeRate: 20 },
    { code: 'RES-05', name: 'Tiện ích', feedbackCount: 980, negativeRate: 34 },
    { code: 'RES-06', name: 'Thanh toán', feedbackCount: 910, negativeRate: 47 },
    { code: 'RES-07', name: 'Gửi phản ánh', feedbackCount: 780, negativeRate: 39 },
    { code: 'RES-08', name: 'Thay đổi căn hộ', feedbackCount: 240, negativeRate: 15 },
  ],
  'STG-06': [ // Vận hành
    { code: 'OPS-01', name: 'Bảo trì tòa nhà định kỳ', feedbackCount: 950, negativeRate: 32 },
    { code: 'OPS-02', name: 'Hội nghị cư dân & BQT', feedbackCount: 896, negativeRate: 38 },
  ],
};

