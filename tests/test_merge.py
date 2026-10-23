from passive_resume_extractor.merge import merge_extracted_fields


def test_scalar_overwrite_keeps_other_fields():
    existing = {"name": "张三", "target_position": "产品经理"}
    merge_extracted_fields(existing, {"target_position": "后端开发"})
    assert existing["target_position"] == "后端开发"
    assert existing["name"] == "张三"


def test_dict_merge():
    existing = {"hard_skills": {"Java": "熟练"}}
    merge_extracted_fields(existing, {"hard_skills": {"Python": "精通"}})
    assert existing["hard_skills"] == {"Java": "熟练", "Python": "精通"}


def test_list_append_dedupes():
    existing = {"certificates": ["四级"]}
    merge_extracted_fields(existing, {"certificates": ["四级", "软考"]})
    assert existing["certificates"] == ["四级", "软考"]


def test_repeating_add_entry():
    existing = {"education_list": []}
    merge_extracted_fields(
        existing,
        {"education_list": [{"_op": "add", "school": "某大学", "major": "计算机"}]},
    )
    assert existing["education_list"] == [{"school": "某大学", "major": "计算机"}]


def test_repeating_update_matching_entry():
    existing = {
        "education_list": [
            {"school": "某大学", "major": "计算机", "degree": "本科"}
        ]
    }
    merge_extracted_fields(
        existing,
        {
            "education_list": [
                {"_op": "update", "_match": {"school": "某大学"}, "gpa": "3.8"}
            ]
        },
    )
    entry = existing["education_list"][0]
    assert entry["gpa"] == "3.8"
    assert entry["major"] == "计算机"  # untouched


def test_empty_delta_ignored():
    existing = {"name": "张三"}
    merge_extracted_fields(existing, {})
    merge_extracted_fields(existing, {"name": ""})
    assert existing == {"name": "张三"}
