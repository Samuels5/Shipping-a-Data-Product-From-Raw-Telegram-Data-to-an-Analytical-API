-- Test that ensures engagement rate is within reasonable bounds (0-100%)
-- This test should return 0 rows to pass

select *
from {{ ref('fct_messages') }}
where engagement_rate < 0 or engagement_rate > 100
