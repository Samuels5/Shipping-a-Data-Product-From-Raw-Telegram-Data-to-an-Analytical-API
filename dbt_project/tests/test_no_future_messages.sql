-- Test that ensures no messages from the future
-- This test should return 0 rows to pass

select *
from {{ ref('fct_messages') }}
where message_date > current_timestamp
