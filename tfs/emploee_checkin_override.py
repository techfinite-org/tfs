import frappe
from datetime import datetime, timedelta

def get_checkin_shifts(self, method, now):
    employee_shift_assignment = frappe.get_all('Shift Assignment', filters={'employee': self.employee, 'start_date': now.date()}, fields=['employee', 'shift_type','start_date'])
    if not employee_shift_assignment:
        employee = frappe.get_doc('Employee', self.employee)
        shift_group = employee.custom_shift_group
        shifts = frappe.get_all('Shift Type', filters={'custom_shift_group': shift_group}, fields=['name', 'start_time'])
        shifts.sort(key=lambda x: datetime.strptime(str(x.start_time), '%H:%M:%S').time())
        next_shift = {}
        curr_shift = {}
        if shifts:
            curr_shift = shifts[0]
            for shift in shifts:
            #shift_start_time = datetime.strptime(str(shift.start_time), '%H:%M:%S').time()
                if shift.start_time < timedelta(hours=now.hour, minutes=now.minute, seconds=now.second):
                    curr_shift = shift
                else:
                    next_shift = shift
                    return curr_shift, next_shift
            if not next_shift:
                return curr_shift, None
    return None, None
    
def assign_shift(self, method):
    now = frappe.utils.get_datetime(self.time)
    curr_shift, next_shift = get_checkin_shifts(self, method, now)
    print(f"Current Shift :{ curr_shift }, Next Shift: { next_shift }, current_time{ now }")
    shift = curr_shift
    if shift:
        if not next_shift or ((timedelta(hours=now.hour, minutes=now.minute, seconds=now.second) - curr_shift.start_time) < (next_shift.start_time - timedelta(hours=now.hour, minutes=now.minute, seconds=now.second))):
            shift = curr_shift
        else:
            shift = next_shift
        
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