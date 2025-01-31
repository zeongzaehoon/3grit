"use client"

import { useEffect, useRef, useState } from 'react'

declare global {
  interface Window {
    kakao: any;
  }
}

interface Place {
  place_name: string;
  road_address_name?: string;
  address_name: string;
  phone: string;
  x: string;
  y: string;
}

export default function RestaurantMap() {
  const mapContainer = useRef<HTMLDivElement>(null);
  const [keyword, setKeyword] = useState('판교 맛집');
  const [map, setMap] = useState<any>(null);
  const [markers, setMarkers] = useState<any[]>([]);
  const [places, setPlaces] = useState<Place[]>([]);
  const [infowindow, setInfowindow] = useState<any>(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(0);

  useEffect(() => {
    const loadKakaoMapScript = () => {
      const script = document.createElement('script');
      script.async = true;
      script.src = `//dapi.kakao.com/v2/maps/sdk.js?appkey=${import.meta.env.VITE_KAKAO_MAP_APP_KEY}&libraries=services&autoload=false`;
      script.onload = () => {
        window.kakao.maps.load(() => {
          initializeMap();
        });
      };
      document.head.appendChild(script);
    };

    const initializeMap = () => {
      if (window.kakao && mapContainer.current) {
        const options = {
          center: new window.kakao.maps.LatLng(37.39, 127.11),
          level: 3
        };

        const mapInstance = new window.kakao.maps.Map(mapContainer.current, options);
        const infowindowInstance = new window.kakao.maps.InfoWindow({ zIndex: 1 });
        
        setMap(mapInstance);
        setInfowindow(infowindowInstance);
        
        // 초기 검색 실행
        searchPlaces(mapInstance, infowindowInstance, keyword);
      }
    };

    if (window.kakao) {
      initializeMap();
    } else {
      loadKakaoMapScript();
    }
  }, []);

  const removeMarkers = () => {
    markers.forEach(marker => marker.setMap(null));
    setMarkers([]);
  };

  const searchPlaces = (mapInstance: any, infowindowInstance: any, searchKeyword: string, page = 1) => {
    const ps = new window.kakao.maps.services.Places();
    
    ps.keywordSearch(searchKeyword, 
      (data: Place[], status: any, pagination: any) => {
        if (status === window.kakao.maps.services.Status.OK) {
          setTotalPages(pagination.last);
          setCurrentPage(pagination.current);
          const bounds = new window.kakao.maps.LatLngBounds();
          removeMarkers();
          
          const newMarkers = data.map((place, index) => {
            const position = new window.kakao.maps.LatLng(place.y, place.x);
            const marker = new window.kakao.maps.Marker({
              position,
              map: mapInstance,
            });

            // 마커 이벤트 리스너
            window.kakao.maps.event.addListener(marker, 'mouseover', () => {
              infowindowInstance.setContent(
                `<div style="padding:5px;font-size:12px;">${place.place_name}</div>`
              );
              infowindowInstance.open(mapInstance, marker);
            });

            window.kakao.maps.event.addListener(marker, 'mouseout', () => {
              infowindowInstance.close();
            });

            bounds.extend(position);
            return marker;
          });

          setMarkers(newMarkers);
          setPlaces(data);
          mapInstance.setBounds(bounds);
        } else if (status === window.kakao.maps.services.Status.ZERO_RESULT) {
          alert('검색 결과가 존재하지 않습니다.');
        } else if (status === window.kakao.maps.services.Status.ERROR) {
          alert('검색 중 오류가 발생했습니다.');
        }
      },
      { page }
    );
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (map && infowindow) {
      if (!keyword.trim()) {
        alert('키워드를 입력해주세요!');
        return;
      }
      searchPlaces(map, infowindow, keyword);
    }
  };

  const handleListItemHover = (index: number) => {
    if (infowindow && markers[index]) {
      infowindow.setContent(
        `<div style="padding:5px;font-size:12px;">${places[index].place_name}</div>`
      );
      infowindow.open(map, markers[index]);
    }
  };

  const handleListItemClick = (index: number) => {
    if (map && markers[index]) {
      // 해당 위치로 지도 중심 이동
      const position = markers[index].getPosition();
      map.setCenter(position);
      
      // 줌 레벨 설정 (1: 가장 가깝게, 14: 가장 멀리)
      map.setLevel(3);  // 적당한 줌 레벨로 설정
      
      // 인포윈도우 표시
      infowindow?.setContent(
        `<div style="padding:5px;font-size:12px;">${places[index].place_name}</div>`
      );
      infowindow?.open(map, markers[index]);
    }
  };

  return (
    <div className="bg-white shadow sm:rounded-lg p-6">
      <h2 className="text-lg font-medium text-gray-900 mb-4">HOT PLACE MAP</h2>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="md:col-span-2">
          <div 
            ref={mapContainer} 
            className="w-full h-[600px] rounded-lg"
          />
        </div>
        
        <div className="bg-white border rounded-lg">
          <div className="p-4 border-b">
            <form onSubmit={handleSearch}>
              <div className="flex gap-2">
                <input
                  type="text"
                  value={keyword}
                  onChange={(e) => setKeyword(e.target.value)}
                  placeholder="검색어를 입력하세요"
                  className="flex-1 rounded-md border border-gray-300 px-3 py-2 focus:border-indigo-500 focus:ring-indigo-500"
                />
                <button
                  type="submit"
                  className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                >
                  검색
                </button>
              </div>
            </form>
          </div>
          
          <ul className="divide-y divide-gray-200 max-h-[500px] overflow-y-auto">
            {places.map((place, index) => (
              <li
                key={index}
                className="p-4 hover:bg-gray-50 cursor-pointer"
                onClick={() => handleListItemClick(index)}
                onMouseEnter={() => handleListItemHover(index)}
                onMouseLeave={() => infowindow?.close()}
              >
                <div className="flex items-start space-x-3">
                  <div className="flex-shrink-0 w-6 h-6 bg-indigo-600 text-white rounded-full flex items-center justify-center text-sm">
                    {(currentPage - 1) * 15 + index + 1}
                  </div>
                  <div>
                    <h3 className="text-sm font-medium text-gray-900">{place.place_name}</h3>
                    {place.road_address_name && (
                      <p className="text-sm text-gray-500">{place.road_address_name}</p>
                    )}
                    <p className="text-sm text-gray-500">{place.address_name}</p>
                    {place.phone && (
                      <p className="text-sm text-gray-500">{place.phone}</p>
                    )}
                  </div>
                </div>
              </li>
            ))}
          </ul>
          <div className="p-4 border-t flex justify-center gap-2">
            {Array.from({ length: totalPages }, (_, i) => (
              <button
                key={i + 1}
                onClick={() => searchPlaces(map, infowindow, keyword, i + 1)}
                className={`px-3 py-1 rounded ${
                  currentPage === i + 1 
                    ? 'bg-indigo-600 text-white' 
                    : 'bg-gray-100 text-gray-700'
                }`}
              >
                {i + 1}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
} 