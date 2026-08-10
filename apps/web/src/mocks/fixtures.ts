import {
  ImportJob,
  AnalyticsSummary,
  TrendResponse,
  BreakdownResponse,
  FeedbackListResponse,
  FeedbackDetail,
} from '../client/types';

export const MOCK_IMPORT_JOBS: Record<string, ImportJob> = {
  'job_9842a1b7': {
    import_job_id: 'job_9842a1b7',
    status: 'VALIDATED',
    filename: 'trusted_feedback_july_2026.csv',
    total_rows: 9850,
    uploaded_at: '2026-08-10T14:00:00Z',
    counts: {
      total_rows: 9850,
      valid_rows: 9700,
      invalid_rows: 150,
      duplicate_rows: 0,
    },
    errors_sample: [
      {
        row_number: 42,
        column_name: 'created_at',
        error_code: 'INVALID_TIMESTAMP',
        message: 'Timestamp must be ISO-8601 compliant (e.g. 2026-08-10T14:00:00Z)',
      },
      {
        row_number: 108,
        column_name: 'location_code',
        error_code: 'UNKNOWN_LOCATION',
        message: 'Location code LOC_INVALID is not defined in active taxonomy',
      },
    ],
    can_execute: true,
  },
};

export const MOCK_SUMMARY: AnalyticsSummary = {
  snapshot_token: 'snap_20260810_150000',
  metrics: {
    total_feedback_volume: 9700,
    negative_feedback_volume: 1398,
    negative_rate: 0.1441,
    sentiment_unknown_rate: 0.021,
    high_severity_count: 342,
    validation_pass_rate: 0.9847,
  },
};

export const MOCK_TREND: TrendResponse = {
  snapshot_token: 'snap_20260810_150000',
  points: [
    { date: '2026-08-01', total_count: 950, negative_count: 120, negative_rate: 0.1263 },
    { date: '2026-08-02', total_count: 1100, negative_count: 180, negative_rate: 0.1636 },
    { date: '2026-08-03', total_count: 1050, negative_count: 140, negative_rate: 0.1333 },
    { date: '2026-08-04', total_count: 1250, negative_count: 210, negative_rate: 0.1680 },
    { date: '2026-08-05', total_count: 1400, negative_count: 195, negative_rate: 0.1392 },
    { date: '2026-08-06', total_count: 1300, negative_count: 175, negative_rate: 0.1346 },
    { date: '2026-08-07', total_count: 1200, negative_count: 168, negative_rate: 0.1400 },
    { date: '2026-08-08', total_count: 1450, negative_count: 210, negative_rate: 0.1448 },
  ],
};

export const MOCK_BREAKDOWN_SERVICE: BreakdownResponse = {
  dimension: 'service',
  snapshot_token: 'snap_20260810_150000',
  segments: [
    { key: 'SRV_SUPPORT', label: 'Hỗ Trợ Khách Hàng', total_count: 4812, negative_count: 820 },
    { key: 'SRV_BILLING', label: 'Thanh Toán & Hóa Đơn', total_count: 2540, negative_count: 410 },
    { key: 'SRV_FACILITY', label: 'Bảo Trì Tòa Nhà & Hạ Tầng', total_count: 1500, negative_count: 128 },
    { key: 'SRV_SECURITY', label: 'An Ninh & Thẻ Từ', total_count: 848, negative_count: 40 },
  ],
};

export const MOCK_BREAKDOWN_LOCATION: BreakdownResponse = {
  dimension: 'location',
  snapshot_token: 'snap_20260810_150000',
  segments: [
    { key: 'LOC_BLDG_A', label: 'Tòa Nhà A - Khối Văn Phòng', total_count: 4100, negative_count: 650 },
    { key: 'LOC_BLDG_B', label: 'Tòa Nhà B - Trung Tâm Thương Mại', total_count: 3200, negative_count: 490 },
    { key: 'LOC_BLDG_C', label: 'Tòa Nhà C - Khu Căn Hộ', total_count: 2400, negative_count: 258 },
  ],
};

export const MOCK_BREAKDOWN_SEVERITY: BreakdownResponse = {
  dimension: 'severity',
  snapshot_token: 'snap_20260810_150000',
  segments: [
    { key: 'LOW', label: 'Mức Thấp (Low)', total_count: 6200, negative_count: 450 },
    { key: 'MEDIUM', label: 'Mức Trung Bình (Medium)', total_count: 3158, negative_count: 606 },
    { key: 'HIGH', label: 'Mức Cao (High)', total_count: 290, negative_count: 290 },
    { key: 'CRITICAL', label: 'Nghiêm Trọng (Critical)', total_count: 52, negative_count: 52 },
  ],
};

export const MOCK_FEEDBACK_ITEMS: FeedbackListResponse = {
  items: [
    {
      feedback_item_id: 'fb_item_98214',
      created_at: '2026-08-10T14:20:00Z',
      service_name: 'Hỗ Trợ Khách Hàng',
      location_name: 'Tòa Nhà A - Tầng 3',
      sentiment: 'NEGATIVE',
      severity: 'HIGH',
      masked_text: 'Khách hàng phản ánh quầy lễ tân *** chậm trễ hỗ trợ làm thẻ cư dân mới, mất hơn 45 phút...',
    },
    {
      feedback_item_id: 'fb_item_98215',
      created_at: '2026-08-10T13:45:00Z',
      service_name: 'Thanh Toán & Hóa Đơn',
      location_name: 'Tòa Nhà B - Tầng 1',
      sentiment: 'NEGATIVE',
      severity: 'HIGH',
      masked_text: 'Hệ thống ứng dụng thông báo sai số tiền phí dịch vụ tháng 8, khách hàng cư dân *** yêu cầu kiểm tra lại...',
    },
    {
      feedback_item_id: 'fb_item_98216',
      created_at: '2026-08-10T11:10:00Z',
      service_name: 'Bảo Trì Tòa Nhà & Hạ Tầng',
      location_name: 'Tòa Nhà C - Thang máy 02',
      sentiment: 'NEGATIVE',
      severity: 'CRITICAL',
      masked_text: 'Thang máy 02 bị giật và dừng đột ngột ở tầng 12, ban quản lý *** cần cử kỹ thuật kiểm tra gấp...',
    },
    {
      feedback_item_id: 'fb_item_98217',
      created_at: '2026-08-09T16:00:00Z',
      service_name: 'Hỗ Trợ Khách Hàng',
      location_name: 'Tòa Nhà A - Sảnh Chính',
      sentiment: 'POSITIVE',
      severity: 'LOW',
      masked_text: 'Nhân viên *** nhiệt tình hướng dẫn khách đăng ký gửi xe sự kiện nhanh chóng.',
    },
  ],
  next_cursor: 'cursor_eyJpZCI6OTgyMTd9',
  has_more: true,
};

export const MOCK_FEEDBACK_DETAIL: Record<string, FeedbackDetail> = {
  'fb_item_98214': {
    feedback_item_id: 'fb_item_98214',
    created_at: '2026-08-10T14:20:00Z',
    service_name: 'Hỗ Trợ Khách Hàng',
    issue_name: 'Thời gian chờ đợi dài',
    location_name: 'Tòa Nhà A - Tầng 3',
    sentiment: 'NEGATIVE',
    severity: 'HIGH',
    masked_text: 'Khách hàng phản ánh quầy lễ tân *** chậm trễ hỗ trợ làm thẻ cư dân mới, mất hơn 45 phút...',
    provenance: {
      import_job_id: 'job_9842a1b7',
      source_reference: 'trusted_feedback_july_2026.csv',
      row_index: 42,
      decision: 'SOURCE_TRUSTED',
      committed_at: '2026-08-10T14:05:00Z',
    },
  },
};
