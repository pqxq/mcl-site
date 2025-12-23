from django.shortcuts import render
from .models import Lesson, ClassGroup, Day, LESSON_TIMES

def schedule_view(request):
    """Display the schedule/timetable page"""
    week_filter = request.GET.get('week', '1')  # Default to week 1
    
    # Get all class groups
    class_groups = ClassGroup.objects.all()
    
    # Get lessons for the specific week
    lessons = Lesson.objects.select_related('subject', 'class_group').order_by('day', 'para_number', 'para_part')
    
    if week_filter:
        lessons = lessons.filter(week=int(week_filter))
    
    # Structure data: {day_name: {lesson_num: {time: X, lessons: {class_id: [lessons]}}}}
    schedule_data = {}
    
    for day_choice in Day.choices:
        day_value, day_name = day_choice
        day_lessons = lessons.filter(day=day_value)
        
        if day_lessons.exists():
            lessons_by_num = {}
            for lesson in day_lessons:
                # Map para and part to absolute lesson number 1-8
                if lesson.para_part == 0: # Full
                    nums = [lesson.para_number * 2 - 1, lesson.para_number * 2]
                elif lesson.para_part == 1: # 1st half
                    nums = [lesson.para_number * 2 - 1]
                else: # 2nd half
                    nums = [lesson.para_number * 2]
                
                for i, num in enumerate(nums):
                    if num not in lessons_by_num:
                        para_map = {1: 'I', 2: 'I', 3: 'II', 4: 'II', 5: 'III', 6: 'III', 7: 'IV', 8: 'IV'}
                        para_label = para_map.get(num, '')
                        
                        lessons_by_num[num] = {
                            'time': LESSON_TIMES.get(num, ''),
                            'para': para_label,
                            'lessons': {} # class_id -> list of lesson_info
                        }
                    
                    if lesson.class_group_id not in lessons_by_num[num]['lessons']:
                        lessons_by_num[num]['lessons'][lesson.class_group_id] = []
                    
                    lesson_info = {
                        'subject': lesson.subject,
                        'cabinet': lesson.cabinet,
                        'sub_group': lesson.sub_group,
                        'rowspan': 2 if lesson.para_part == 0 and i == 0 else 1,
                        'skip': True if lesson.para_part == 0 and i == 1 else False
                    }
                    
                    lessons_by_num[num]['lessons'][lesson.class_group_id].append(lesson_info)
            
            # Sort by lesson number and calculate rowspans for Para
            sorted_lessons = dict(sorted(lessons_by_num.items()))
            last_para = None
            for num, row in sorted_lessons.items():
                if row['para'] != last_para:
                    row['show_para'] = True
                    row['para_rowspan'] = sum(1 for r in sorted_lessons.values() if r['para'] == row['para'])
                    last_para = row['para']
                else:
                    row['show_para'] = False
            
            schedule_data[day_name] = sorted_lessons
    
    context = {
        'schedule_data': schedule_data,
        'class_groups': class_groups,
        'current_week': week_filter,
    }
    
    return render(request, 'schedule/schedule_page.html', context)
