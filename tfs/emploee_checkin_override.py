import frappe
from datetime import datetime, timedelta


def get_checkin_shifts(self, method, now):
        employee = frappe.get_doc('Employee', self.employee)
        shift_group = employee.custom_shift_group
        if shift_group:
            shifts = frappe.get_all('Shift Type', filters={'custom_shift_group': shift_group}, fields=['name', 'start_time', 'end_time','begin_check_in_before_shift_start_time','allow_check_out_after_shift_end_time','late_entry_grace_period'])
            shifts.sort(key=lambda x: datetime.strptime(str(x.start_time), '%H:%M:%S').time())
            next_shift = {}
            curr_shift = {}
            if shifts:
                curr_shift = shifts[0]
                for shift in shifts:
                # shift_start_time = datetime.strptime(str(shift.start_time), '%H:%M:%S').time()
                    if shift.start_time < timedelta(hours=now.hour, minutes=now.minute, seconds=now.second):
                        curr_shift = shift
                    else:
                        next_shift = shift
                        return curr_shift, next_shift
                if not next_shift:
                    return curr_shift, None
    
    
def assign_shift(self, method):
    if not self.shift:
        now = frappe.utils.get_datetime(self.time)
        now_date = now.date()
        curr_shift, next_shift = get_checkin_shifts(self, method, now)
        # print(f"Current Shift :{ curr_shift }, Next Shift: { next_shift }, current_time{ now }")
        shift = curr_shift
        if shift:
            if not next_shift or ((timedelta(hours=now.hour, minutes=now.minute, seconds=now.second) - curr_shift.start_time) < (next_shift.start_time - timedelta(hours=now.hour, minutes=now.minute, seconds=now.second))):
                shift = curr_shift
            else:
                shift = next_shift
            self.shift = shift.name
            # self.shift_start = shift.start_time
            shift_start = frappe.utils.get_datetime(f"{now_date} {shift.start_time}")
            shift_end = frappe.utils.get_datetime(f"{now_date} {shift.end_time}")
            actual_start = shift_start - timedelta(
                            minutes=shift.begin_check_in_before_shift_start_time
                            )
            actual_end = shift_end + timedelta(minutes=shift.allow_check_out_after_shift_end_time)
            time_format = "%Y-%m-%d %H:%M:%S"
            if isinstance(self.time, datetime):
                self_time_str = self.time.strftime(time_format)
            else:    
                self_time_str = self.time
            # print("---------self_time_str----------",self_time_str)    
            self_time_datetime = datetime.strptime(self_time_str, time_format)
            shift_start_and_grace = shift_start + timedelta(minutes=shift.late_entry_grace_period)
            late_entry = self_time_datetime - shift_start_and_grace
            # Check if the late entry is negative, and adjust accordingly
            if late_entry.total_seconds() < 0:
            # Handle negative late entry, set custom_late_entry to a default value or handle it as needed
                self.custom_late_entry = 0  # Replace with your desired default value
            else:
                hours, remainder_minutes = divmod(late_entry.seconds, 3600)
                minutes = remainder_minutes // 60

                if hours > 0:
                   self.custom_late_entry = f"{hours}:{minutes} Hr"
                else:
                     self.custom_late_entry = f"{minutes} Min"

           
            # print("late_entry",late_entry)
            self.shift_start = shift_start
            self.shift_end = shift_end
            self.shift_actual_start = actual_start
            self.shift_actual_end = actual_end
            self.custom_entry_number = 1
            create_shift_assignment(self.employee, shift.name, now)
			
def create_shift_assignment(employee, shift_type, now):
    shift_assignment = frappe.new_doc("Shift Assignment")
    shift_assignment.employee = employee
    shift_assignment.shift_type = shift_type
    shift_assignment.start_date = now.date()
    shift_assignment.end_date = now.date()
    shift_assignment.save()
    shift_assignment.submit()
    return shift_assignment