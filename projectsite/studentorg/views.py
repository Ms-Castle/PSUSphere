from django.shortcuts import render

from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from studentorg.models import Organization, OrgMember, Student, College, Program
from studentorg.forms import OrganizationForm
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from typing import Any
from django.db.models.query import QuerySet
from django.db.models import Q

from django.db import connection
from django.http import JsonResponse
from django.db.models.functions import ExtractMonth

from django.db.models import Count
from datetime import datetime

# Home Page View
@method_decorator(login_required, name='dispatch')
class HomePageView(ListView):
    model = Organization
    context_object_name = 'home'
    template_name = 'home.html'

# Organization Views
class OrganizationList(ListView):
    model = Organization
    context_object_name = 'organization'
    template_name = 'org_list.html'
    paginate_by = 5

    def get_queryset(self, *args, **kwargs):
        qs = super(OrganizationList, self).get_queryset(*args, **kwargs)
        if self.request.GET.get("q") != None:
            query = self.request.GET.get('q')
            qs = qs.filter(Q(name__icontains=query) |
                            Q(description__icontains=query))
        return qs

class OrganizationCreateView(CreateView):
    model = Organization
    form_class = OrganizationForm
    template_name = 'org_add.html'
    success_url = reverse_lazy('organization-list')

class OrganizationUpdateView(UpdateView):
    model = Organization
    form_class = OrganizationForm
    template_name = 'org_edit.html'
    success_url = reverse_lazy('organization-list')

class OrganizationDeleteView(DeleteView):
    model = Organization
    template_name = 'org_del.html'
    success_url = reverse_lazy('organization-list')

# OrgMember Views
class OrgMemberList(ListView):
    model = OrgMember
    context_object_name = 'orgmember'
    template_name = 'orgmember_list.html'
    paginate_by = 5

    def get_queryset(self, *args, **kwargs):
        qs = super(OrgMemberList, self).get_queryset(*args, **kwargs)
        if self.request.GET.get("q") != None:
            query = self.request.GET.get('q')
            qs = qs.filter(Q(student__lastname__icontains=query) |
                            Q(organization__name__icontains=query))
        return qs

class OrgMemberCreateView(CreateView):
    model = OrgMember
    fields = '__all__'
    template_name = 'orgmember_add.html'
    success_url = reverse_lazy('orgmember-list')

class OrgMemberUpdateView(UpdateView):
    model = OrgMember
    fields = '__all__'
    template_name = 'orgmember_edit.html'
    success_url = reverse_lazy('orgmember-list')

class OrgMemberDeleteView(DeleteView):
    model = OrgMember
    template_name = 'orgmember_del.html'
    success_url = reverse_lazy('orgmember-list')

# Student Views
class StudentList(ListView):
    model = Student
    context_object_name = 'student'
    template_name = 'student_list.html'
    paginate_by = 5

    def get_queryset(self, *args, **kwargs):
        qs = super(StudentList, self).get_queryset(*args, **kwargs)
        if self.request.GET.get("q") != None:
            query = self.request.GET.get('q')
            qs = qs.filter(Q(student_id__icontains=query) |
                            Q(lastname__icontains=query) |
                            Q(program__prog_name__icontains=query) |
                            Q(firstname__icontains=query))
        return qs

class StudentCreateView(CreateView):
    model = Student
    fields = '__all__'
    template_name = 'student_add.html'
    success_url = reverse_lazy('student-list')

class StudentUpdateView(UpdateView):
    model = Student
    fields = '__all__'
    template_name = 'student_edit.html'
    success_url = reverse_lazy('student-list')

class StudentDeleteView(DeleteView):
    model = Student
    template_name = 'student_del.html'
    success_url = reverse_lazy('student-list')

# College Views
class CollegeList(ListView):
    model = College
    context_object_name = 'college'
    template_name = 'college_list.html'
    paginate_by = 5

    def get_queryset(self, *args, **kwargs):
        qs = super(CollegeList, self).get_queryset(*args, **kwargs)
        if self.request.GET.get("q") != None:
            query = self.request.GET.get('q')
            qs = qs.filter(college_name__icontains=query)
        return qs

class CollegeCreateView(CreateView):
    model = College
    fields = '__all__'
    template_name = 'college_add.html'
    success_url = reverse_lazy('college-list')

class CollegeUpdateView(UpdateView):
    model = College
    fields = '__all__'
    template_name = 'college_edit.html'
    success_url = reverse_lazy('college-list')

class CollegeDeleteView(DeleteView):
    model = College
    template_name = 'college_del.html'
    success_url = reverse_lazy('college-list')

# Program Views
class ProgramList(ListView):
    model = Program
    context_object_name = 'program'
    template_name = 'program_list.html'
    paginate_by = 5

    def get_queryset(self, *args, **kwargs):
        qs = super(ProgramList, self).get_queryset(*args, **kwargs)
        if self.request.GET.get("q") != None:
            query = self.request.GET.get('q')
            qs = qs.filter(Q(prog_name__icontains=query) |
                            Q(college__college_name__icontains=query))
        return qs

class ProgramCreateView(CreateView):
    model = Program
    fields = '__all__'
    template_name = 'program_add.html'
    success_url = reverse_lazy('program-list')

class ProgramUpdateView(UpdateView):
    model = Program
    fields = '__all__'
    template_name = 'program_edit.html'
    success_url = reverse_lazy('program-list')

class ProgramDeleteView(DeleteView):
    model = Program
    template_name = 'program_del.html'
    success_url = reverse_lazy('program-list')
    
class ChartView(ListView):
    template_name = 'chart.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
    
    def get_queryset(self, *args, **kwargs):
        pass
    
def LineCount(request):
    current_year = datetime.now().year

    # Get all colleges
    colleges = College.objects.all()
    month_names = {
        1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun', 7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'
    }
    months = list(month_names.values())

    # Prepare result: {college_name: {month: count, ...}, ...}
    result = {}
    for college in colleges:
        result[college.college_name] = {month: 0 for month in months}

    # Query OrgMembers joined this year, grouped by college and month
    data = (
        OrgMember.objects
        .filter(date_joined__year=current_year)
        .values('student__program__college__college_name')
        .annotate(month=ExtractMonth('date_joined'), count=Count('id'))
        .order_by('student__program__college__college_name', 'month')
    )

    for entry in data:
        college_name = entry['student__program__college__college_name'] or "Unknown"
        month = month_names.get(entry['month'])
        if college_name in result and month:
            result[college_name][month] = entry['count']

    return JsonResponse(result)

def PieCountbyCollege(request):
    data = (
        Student.objects
        .values('program__college__college_name')
        .annotate(count=Count('id'))
        .order_by('program__college__college_name')
    )

    labels = []
    counts = []
    for entry in data:
        labels.append(entry['program__college__college_name'] or "Unknown")
        counts.append(entry['count'])

    return JsonResponse({
        'labels': labels,
        'data': counts,
    })


def MultilineOrgTop3(request):
    # Get top 3 organizations by member count for the current year
    current_year = datetime.now().year

    # Get top 3 orgs by member count
    top_orgs = (
        OrgMember.objects.filter(date_joined__year=current_year)
        .values('organization__name')
        .annotate(total=Count('id'))
        .order_by('-total')[:3]
    )
    top_org_names = [org['organization__name'] for org in top_orgs]

    # Prepare months
    months = [str(i).zfill(2) for i in range(1, 13)]
    month_names = {
        '01': 'Jan', '02': 'Feb', '03': 'Mar', '04': 'Apr', '05': 'May', '06': 'Jun',
        '07': 'Jul', '08': 'Aug', '09': 'Sep', '10': 'Oct', '11': 'Nov', '12': 'Dec'
    }

    # Query member count per org per month
    data = (
        OrgMember.objects.filter(
            date_joined__year=current_year,
            organization__name__in=top_org_names
        )
        .annotate(month=ExtractMonth('date_joined'))
        .values('organization__name', 'month')
        .annotate(count=Count('id'))
        .order_by('organization__name', 'month')
    )

    # Build result dict
    result = {}
    for org in top_org_names:
        result[org] = {month_names[m]: 0 for m in months}

    for entry in data:
        org = entry['organization__name']
        month = str(entry['month']).zfill(2)
        count = entry['count']
        result[org][month_names[month]] = count

    # Ensure always 3 orgs in result
    while len(result) < 3:
        fake_org = f"Organization {len(result) + 1}"
        result[fake_org] = {month_names[m]: 0 for m in months}

    # Sort months for each org
    for org in result:
        result[org] = dict(sorted(result[org].items(), key=lambda x: months.index([k for k, v in month_names.items() if v == x[0]][0])))

    return JsonResponse(result)

def multipleBarByOrgMembers(request):
    current_year = datetime.now().year

    # Get all organizations
    orgs = Organization.objects.values_list('name', flat=True)
    months = [str(i).zfill(2) for i in range(1, 13)]

    # Prepare result: {org_name: {month: 0, ...}, ...}
    result = {}
    for org in orgs:
        result[org] = {month: 0 for month in months}

    # Query OrgMembers joined this year, grouped by org and month
    data = (
        OrgMember.objects
        .filter(date_joined__year=current_year)
        .values('organization__name')
        .annotate(month=ExtractMonth('date_joined'), count=Count('id'))
        .order_by('organization__name', 'month')
    )

    for entry in data:
        org_name = entry['organization__name']
        month = str(entry['month']).zfill(2)
        count = entry['count']
        if org_name in result and month in result[org_name]:
            result[org_name][month] = count

    # Sort months for each org
    for org in result:
        result[org] = dict(sorted(result[org].items()))

    return JsonResponse(result)
