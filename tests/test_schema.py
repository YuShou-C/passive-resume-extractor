from passive_resume_extractor.schema import (
    ALL_FIELDS,
    FIELDS_BY_MODULE,
    ResumeModule,
    build_flat_profile_for_llm,
    new_empty_resume_data,
    validate_resume_data,
)


def test_all_modules_present():
    assert set(FIELDS_BY_MODULE) == set(ResumeModule)


def test_empty_resume_data_has_all_keys():
    data = new_empty_resume_data()
    assert set(data.keys()) == {f.key for f in ALL_FIELDS}


def test_validate_reports_missing_required_fields():
    data = new_empty_resume_data()
    missing = validate_resume_data(data)
    assert "name" in missing
    assert "target_position" in missing


def test_validate_passes_when_required_filled():
    data = new_empty_resume_data()
    data["name"] = "张三"
    data["target_position"] = "后端开发工程师"
    data["gender"] = "男"
    data["phone"] = "13800000000"
    data["email"] = "zhangsan@example.com"
    # education / work / project 为重复组，给一条记录
    data["education_list"] = [{"school": "某大学", "major": "计算机", "degree": "本科", "education_period": "2020-2024"}]
    data["work_experience_list"] = [{"company": "某公司", "department": "研发", "position": "开发", "work_period": "2024-", "work_responsibilities": "负责后端"}]
    data["project_experience_list"] = [{"project_name": "某项目", "project_role": "开发", "project_period": "2023", "project_background": "b", "project_content": "c", "project_result": "r"}]
    missing = validate_resume_data(data)
    assert missing == []


def test_flat_profile_includes_known_info():
    data = new_empty_resume_data()
    data["target_position"] = "后端开发工程师"
    data["name"] = "张三"
    text = build_flat_profile_for_llm(data)
    assert "后端开发工程师" in text
    assert "张三" in text
