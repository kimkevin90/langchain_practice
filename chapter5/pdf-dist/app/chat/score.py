import random
from app.chat.redis import client

def random_component_by_score(component_type, component_map):
    print('새로운 대화 시작 random_component_by_score!')
    # Make sure component_type is 'llm', 'retriever', or 'memory'
    if component_type not in ["llm", "retriever", "memory"]:
        raise ValueError("Invalid component_type")

    # From redis, get the hash containing the sum total scores for the given commponent_type
    values = client.hgetall(f"{component_type}_score_values")
    # print('values : ',values)
    # From redis, get the hash containing the number of times each component has been voted on
    counts = client.hgetall(f"{component_type}_score_counts")
    # print('counts : ',counts)
    # Get all the valid component names from the component map
    names = component_map.keys()

    # Loop over those valid names and use them to calculate the average score for each
    # Add average score to a dictionary
    avg_scores = {}
    for name in names:
        # Redis의 결과는 숫자라도 문자열로 주므로 타입 지정
        score = int(values.get(name, 1))
        count = int(counts.get(name, 1))
        avg = score / count
        # 최소한의 점수 0.1을 주어 0이 안되도록 하여 가중치를 반영할 수 있도록 한다.
        avg_scores[name] = max(avg, 0.1)

    print('avg_scores : ',avg_scores)
    # Do a weighted random selection
    # 예를들어, pincone_3, pincone_2, pincone_1의 score가 각각 다를 경우 임의의 random_val보다 높을 경우 이를 선택
    sum_scores = sum(avg_scores.values())
    random_val = random.uniform(0, sum_scores)
    cumulative = 0
    print('sum_scores : ',sum_scores)
    print('random_val : ',random_val)
    for name, score in avg_scores.items():
        cumulative += score
        if random_val <= cumulative:
            return name
    
    

def score_conversation(
    conversation_id: str, score: float, llm: str, retriever: str, memory: str
) -> None:
    # score는 0또는 1로 기록
    score = min(max(score, 0), 1)

    # llm, retriever, memory에 메시지별 점수와, count를 기록
    client.hincrby("llm_score_values", llm, score)
    client.hincrby("llm_score_counts", llm, 1)

    client.hincrby("retriever_score_values", retriever, score)
    client.hincrby("retriever_score_counts", retriever, 1)

    client.hincrby("memory_score_values", memory, score)
    client.hincrby("memory_score_counts", memory, 1)

# 사용자가 어떤 componentMap에 점수를 많이 줬는지 파악한다.
def get_scores():
    """
    다양한 컴포넌트 유형과 이름에 대한 점수를 langfuse 클라이언트에서 검색하고 정리합니다.
    점수는 중첩된 사전 형식으로 분류 및 집계되며, outer 키는 컴포넌트 유형을 나타내고.
    outer 키는 컴포넌트 유형을, inner 키는 컴포넌트 이름을 나타내며 각 점수는 배열로 나열됩니다.

    이 함수는 langfuse 클라이언트의 스코어 엔드포인트에 액세스하여 스코어를 가져옵니다.
    점수 이름을 JSON으로 파싱할 수 없는 경우 건너뜁니다.

    :return: A dictionary organized by component type and name, containing arrays of scores.

    Example:

        {
            'llm': {
                'chatopenai-3.5-turbo': [score1, score2],
                'chatopenai-4': [score3, score4]
            },
            'retriever': { 'pinecone_store': [score5, score6] },
            'memory': { 'persist_memory': [score7, score8] }
        }
    """
    aggregate = {"llm": {}, "retriever": {}, "memory": {}}

    for component_type in aggregate.keys():
        values = client.hgetall(f"{component_type}_score_values")
        counts = client.hgetall(f"{component_type}_score_counts")

        names = values.keys()

        for name in names:
            score = int(values.get(name, 1))
            count = int(counts.get(name, 1))
            avg = score / count 
            aggregate[component_type][name] = [avg]

    return aggregate